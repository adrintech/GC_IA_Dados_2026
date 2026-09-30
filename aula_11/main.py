import random 

cardapio = {
    "chocolate": 5.0,
    "baunilha": 4.5,
    "morango": 3.5,
    "flocos": 9.0,
}

brindes = ["Canudo", "Copo personalizado", "Gelo", "Badge"]

def mostrar_cardapio():
    print("--CARDAPIO--")

    for sabor, preco in cardapio.items():
        print(f"{sabor}, R${preco}")

def fazer_pedido():
    total = 0.0
    pedido = []
    escolha = ""

    while escolha != "fechar":
        escolha = input("\nEscolha o sabor: (digite 'fechar'  para sair)")

        if escolha == "fechar":
            break
        elif escolha in cardapio:
            total += cardapio[escolha]
            pedido.append(escolha)
            print(f"{escolha} adicionado!")
        else:
            print("Sabor não está no cardapio.")
        
    return pedido, total



mostrar_cardapio()
pedido, total = fazer_pedido()

print(f"\nSeu pedido: {pedido}")
print(f"Total: {total:.2f}")

if total > 15:
    print(f"Você ganhou um brinde: {random.choice(brindes)}")

