from prefect import flow, task
from prefect.blocks.system import Secret
from openai import OpenAI


@task
def call_llm(prompt: str):
    # Obtener el secret desde Prefect Cloud
    api_key = Secret.load("openai-api-key").get()

    # Cliente de OpenAI
    client = OpenAI(api_key=api_key)

    # Hacer el prompt
    # Nota: los modelos disponibles en la API de OpenAI cambian con frecuencia
    # (gpt-3.5-turbo ya fue retirado). Verifica en https://platform.openai.com/docs/models
    # cual es el modelo economico vigente antes de usar este script en clase.
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    print(f"Respuesta: {answer}")
    return answer


@flow(log_prints=True)
def llm_flow(prompt: str = "Explica MLOps en una frase"):
    result = call_llm(prompt)
    return result


if __name__ == "__main__":
    llm_flow()
