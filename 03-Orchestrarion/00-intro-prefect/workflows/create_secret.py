from prefect.blocks.system import Secret


# crear
# my_secret_block = Secret(value="shhh!-it's-a-secret")
# my_secret_block.save(name="secret-thing")

# cargar y obtener

# secret_block = Secret.load("secret-thing")
# print(secret_block.get())