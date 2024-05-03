

def sort_dict(result, threshold):
    vals = [
        val 
        for val in result.items()
    ]
    return sorted(vals, key=lambda x:x[1], reverse=True)[:threshold]
