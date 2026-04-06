## Git y GitHub: Instalar, Configurar y Colaborar

### 1) Instalar Git

- macOS:
  - Preferido: `brew install git`
  - O: `xcode-select --install` para obtener el Git de Apple
- Windows:
  - Seguir la guia de: <https://git-scm.com/downloads/win>
  
Verificar:

```bash
git --version
```

### 2) Configurar Git (identidad y valores por defecto)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 3) Configurar claves SSH para GitHub

Antes de ejecutar comandos, vale la pena entender la idea general:

- `ssh-keygen` es el comando que crea una identidad digital para tu computador.
- Esa identidad se compone de 2 claves:
  - una **clave privada**, que se queda en tu computador y no se comparte;
  - una **clave pública**, que sí puedes copiar y registrar en GitHub.
- Este paso se hace para que GitHub pueda reconocer tu computador sin pedir usuario y contraseña en cada operación.
- En palabras simples: es como crear una llave y registrar una copia segura de esa llave en GitHub para demostrar que realmente eres tú.

Generar una nueva clave (ed25519):

```bash
ssh-keygen -t ed25519 -C "you@example.com"
# Presiona Enter para aceptar la ruta por defecto.
# Si quieres, agrega una passphrase: es como una contraseña extra para proteger tu clave privada.
```

Qué significa este comando:

- `ssh-keygen`: genera el par de claves.
- `-t ed25519`: indica el tipo de clave que vamos a crear; es una opción moderna y recomendada.
- `-C "you@example.com"`: agrega una etiqueta para identificar esa clave; normalmente se usa el correo.

Añadir tu clave al agente SSH:

- macOS:

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

- Windows (PowerShell):

```powershell
# Set the sshd service to be started automatically.
Get-Service -Name sshd | Set-Service -StartupType Automatic

# Start the sshd service.
Start-Service sshd
ssh-add $env:USERPROFILE\.ssh\id_ed25519
```

Copia la clave pública y añádela en GitHub → Settings → SSH and GPG keys:

- Aquí debes pegar la clave que termina en `.pub`.
- La clave `.pub` es la pública y se puede compartir.
- La clave que **no** termina en `.pub` es la privada y **no debe compartirse**.

- macOS:

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

- Windows (PowerShell):

```powershell
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub
# Copy the output manually
```

Probar el acceso por SSH:

```bash
ssh -T git@github.com
```

Si todo está bien, GitHub responderá saludándote por tu usuario. Eso confirma que tu computador ya fue reconocido.

### 4) Qué significa cuando sale "Permission denied"

Cuando aparece un mensaje como `Permission denied (publickey)`, normalmente significa:

- GitHub no reconoce la clave pública de tu computador.
- O tu clave privada no fue cargada en el agente SSH.
- O estás intentando conectarte con otra cuenta o con otra clave distinta.

En palabras simples: GitHub te está diciendo "no pude confirmar que este computador tenga permiso para entrar".

Qué revisar:

- Que hayas copiado en GitHub la clave pública correcta.
- Que la clave privada exista en tu computador.
- Que hayas ejecutado `ssh-add` para cargar la clave.
- Que al probar con `ssh -T git@github.com` no aparezcan errores.

### 5) Qué son las "SSH and GPG keys" en GitHub

En GitHub aparecen juntas, pero no sirven para lo mismo:

- **SSH keys**: sirven para autenticar tu computador cuando haces `clone`, `pull` o `push`.
- **GPG keys**: sirven para firmar commits y demostrar que un commit realmente fue creado por ti y no fue alterado.

### 6) Configurar clave GPG para firmar commits (opcional pero recomendado)

¿Por qué firmar commits? Cuando haces un commit, Git solo registra el nombre y correo que
configuraste en el paso 2. Cualquier persona podría poner tu nombre en su configuración y
hacer commits "como si fuera tú". La firma GPG resuelve eso: es una prueba criptográfica
de que el commit realmente salió de tu computador.

En GitHub los commits firmados aparecen con una etiqueta verde **"Verified"**.

#### a) Instalar GPG

- macOS:

```bash
brew install gnupg
```

- Windows:
  - Descargar e instalar desde: <https://www.gnupg.org/download/>
  - O si usas `winget`:

```powershell
winget install GnuPG.GnuPG
```

Verificar:

```bash
gpg --version
```

#### b) Generar una clave GPG

```bash
gpg --full-generate-key
```

El comando te hará varias preguntas. Estas son las respuestas recomendadas:

1. **Tipo de clave**: elige `1` (RSA and RSA). Es la opción por defecto.
2. **Tamaño**: escribe `4096`. GitHub requiere mínimo 4096 bits.
3. **Expiración**: elige `0` (no expira) para simplificar. Siempre puedes revocarla después.
4. **Nombre y correo**: usa **el mismo correo** que configuraste en Git y en GitHub.
5. **Passphrase**: escribe una contraseña que recuerdes. Cada vez que firmes un commit te la pedirá.

#### c) Obtener el ID de tu clave

```bash
gpg --list-secret-keys --keyid-format=long
```

Verás algo como esto:

```
sec   rsa4096/3AA5C34371567BD2 2025-01-01 [SC]
      ABCDEF1234567890ABCDEF1234567890ABCDEF12
uid                 [ultimate] Tu Nombre <you@example.com>
ssb   rsa4096/4BB6D45482678CE3 2025-01-01 [E]
```

El ID de tu clave es la parte después de `rsa4096/`. En este ejemplo: `3AA5C34371567BD2`.

#### d) Exportar la clave pública y subirla a GitHub

```bash
gpg --armor --export 3AA5C34371567BD2
```

Esto imprime un bloque de texto que empieza con `-----BEGIN PGP PUBLIC KEY BLOCK-----` y
termina con `-----END PGP PUBLIC KEY BLOCK-----`.

Cópialo completo (incluyendo esas líneas) y ve a:

**GitHub → Settings → SSH and GPG keys → New GPG key** → pega el bloque → **Add GPG key**.

#### e) Decirle a Git que use tu clave para firmar

```bash
git config --global user.signingkey 3AA5C34371567BD2
git config --global commit.gpgsign true
```

- La primera línea le dice a Git cuál clave usar.
- La segunda línea activa la firma automática en todos tus commits. Así no necesitas acordarte
  de agregar `-S` cada vez.

#### f) Configurar GPG para que pueda pedir la passphrase

En algunos sistemas, GPG necesita saber cómo pedirte la contraseña. Si al hacer commit te
sale un error como `gpg: signing failed: No pinentry`, ejecuta:

- macOS:

```bash
brew install pinentry-mac
echo "pinentry-program $(which pinentry-mac)" >> ~/.gnupg/gpg-agent.conf
gpgconf --kill gpg-agent
```

- Windows: normalmente funciona sin configuración adicional. Si no, reinstala Gpg4win desde
  <https://www.gpg4win.org/>.

#### g) Verificar que todo funciona

```bash
echo "test" | gpg --clearsign
```

Si te pide la passphrase y muestra un bloque firmado, tu GPG está funcionando. Ahora al
hacer `git commit`, el commit quedará firmado automáticamente y aparecerá como **Verified**
en GitHub.

#### Resumen visual de SSH vs GPG

```
SSH  → Para ENTRAR (autenticación)
       Tu computador le dice a GitHub: "Soy yo, déjame hacer push/pull"

GPG  → Para FIRMAR (verificación de autoría)
       Tu commit le dice a GitHub: "Este cambio fue hecho por mí, verificado"
```

### 7) Clonar el repositorio y configurar remotos

```bash
# Clona tu fork
git clone git@github.com:<your-username>/<repo-name>.git
cd <repo-name>
```

### 8) Flujo de trabajo diario

```bash
# Crea una rama para tu trabajo
git checkout -b feature/my-topic

# Realiza tus cambios, añade y commitea
git add -A
git commit -m "Add: tutorial for X"

# Actualiza tu rama con los últimos cambios de main
git fetch upstream
git rebase upstream/main

# Haz push a tu fork
git push -u origin feature/my-topic
```

Abre un Pull Request en GitHub desde tu rama hacia `main`.

### 9) Resolución de problemas comunes

- Permiso SSH denegado: verifica que tu clave esté añadida al agente y a GitHub; ejecuta `ssh -T git@github.com`.
- Errores por saltos de línea en Windows: asegúrate de `core.autocrlf true` y usa PowerShell para scripts `.ps1`.
- Tu rama está desactualizada: ejecuta `git fetch upstream && git rebase upstream/main`.
