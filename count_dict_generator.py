import os

def main():
    for dir in os.listdir('input'):
        if os.path.isdir(f'input/{dir}'):
            json_str = "{\n"
            for filename in os.listdir(f'input/{dir}/front'):
                json_str = f'{json_str}"{filename}":\t1,\n'
            json_str = json_str.rstrip(",\n")
            json_str += "\n}"
        with open(f"input/{dir}/{dir}.json","w") as file:
            file.write(json_str)
            
                
            


if __name__ == "__main__":
    main()