def find_chain(end, start, d, visited = []): # note : the path doesn't have the start
    value = d.get(start, False)
    if value:
        if end in value.keys():
            return [end], [d[start][end]]
        else:
            for node, cert in d[start].items():
                if visited:
                    if node not in visited:
                        visited.append(node)
                        sub_path, sub_chain = find_chain(node, end, d, visited)
                        if sub_chain is not None:
                            return [node]+sub_path, [d[start][node]]+sub_chain
                else: #visited is empty
                    visited.append(node)
                    sub_path, sub_chain = find_chain(node, end, d, visited)
                    if sub_chain is not None:
                        return [node]+sub_path, [d[start][node]]+sub_chain


def verify_chain(start_pub_key, cert_chain):
    for x in cert_chain:
        try:
            if x.verif_certif(start_pub_key):
                start_pub_key = x.x509.public_key()
        except:
            print("Chain certification error, breaking")
            return False
    #print("The chain has been verified")
    return True

