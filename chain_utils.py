def find_chain(end, start, d, visited = []): # note : the path doesn't have the start
    value = d.get(start, False)
    if value:
        if end in value.keys():
            return  [d[start][end]]
        else:
            for node, cert in d[start].items():
                if visited:
                    if node not in visited:
                        visited.append(node)
                        try : sub_path, sub_chain = find_chain(node, end, d, visited)
                        except : sub_chain = None
                        if sub_chain is not None:
                            return  [d[start][node]]+sub_chain
                else: #visited is empty
                    visited.append(node)
                    try : sub_path, sub_chain = find_chain(node, end, d, visited)
                    except : sub_chain = None
                    if sub_chain is not None:
                        return [d[start][node]]+sub_chain
    return None

def verify_chain(start_pub_key, cert_chain):
    for x in cert_chain:
        try:
            if x.verif_certif(start_pub_key):
                start_pub_key = x.x509.public_key()
        except:
            print("Chain certification error, breaking at step ", start_pub_key)
            return False
    #print("The chain has been verified")
    return True

