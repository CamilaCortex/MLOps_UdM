from prefect.variables import Variable


# La primera vez, crea la variable desde la UI de Prefect o con:
#   Variable.set("answer", 28)
var = Variable.get("answer", default=None)

if var is None:
    print("La variable 'answer' no existe todavia. Creala en la UI de Prefect "
          "(Variables) o ejecuta Variable.set('answer', 28) antes de correr este script.")
else:
    print(var)
