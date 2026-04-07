from prefect.variables import Variable


# firt time Variable.set("answer", 28)
var = Variable.get("answer")  # answer is a variable set in the UI or code
print(var)


