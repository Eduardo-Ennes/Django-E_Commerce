def formata_preco(val):
    return f'R${val:.2f}'.replace('.' , ',')

def cart_total_qtd(carrinho):
    cont = 0
    for c in carrinho.values():
        cont += c['quantidade']
    return cont
        
def soma_total(valor):
    cont = 0
    for c in valor.values():
        if c['preco_quantitativo_promocional']:
            cont += c['preco_quantitativo_promocional']
        else:
            cont += c['preco_quantitativo']
    return cont
 
    # Forma do professor 
    # return sum([
    #     item.get('preco_quantitativo_promocional')
    #     if item.get('preco_quantitativo_promocional')
    #     else item.get('preco_quantitativo')
    #     for item
    #     in valor.values()
    # ])




    
        