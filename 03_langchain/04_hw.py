import math
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableSequence, RunnablePassthrough

a, b, c = map(float, input("Введите вещественные коэффициенты через пробел: ").split())
data = {"a": a, "b": b, "c": c}
def check_d(data: dict[str, float]):
    if data["D"] == 0:
        return RunnableLambda(lambda data: {"x0":-data["b"] / 2 / data["a"]})
    elif data["D"] < 0:
        return RunnableLambda(lambda data: "нет корней")
    else:
        x1_runnable = RunnableLambda(lambda data: (-data["b"] + math.sqrt(data["D"])) / 2 / a)
        x2_runnable = RunnableLambda(lambda data: (-data["b"] - math.sqrt(data["D"])) / 2 / a)
        # {"x1": x1_runnable, "x2": x2_runnable}
        return RunnableParallel(x1=x1_runnable, x2=x2_runnable)

disc_runnable = RunnableLambda(lambda data: data["b"] ** 2 - 4 * data["a"] * data["c"])
chain = RunnablePassthrough.assign(D=disc_runnable)
check_disc_runnable = RunnableLambda(check_d)
solve_equation_runnable = RunnableSequence(chain, check_disc_runnable) # disc_runnable | check_disc_runnable

print(solve_equation_runnable.invoke(data))
chain.get_graph().print_ascii()