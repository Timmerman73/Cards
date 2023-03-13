import os

def main():
    """Generates .json files for echt directory in input.
    These files decide how many times each card gets printed
    """
    for dir in os.listdir('input'):
        if os.path.isdir(f'input/{dir}'):
            json_str = "{\n"
            for filename in os.listdir(f'input/{dir}/front'):
                json_str = f'{json_str}"{filename}":\t1,\n'
            json_str = json_str.rstrip(",\n")
            json_str += "\n}"
        overwrite = True
        if os.path.exists(f"input/{dir}/{dir}.json"):
            overwrite = input(f"input/{dir}/{dir}.json already exists do you want to overwrite it? Y/n ").upper() == "Y"
        if overwrite:
            with open(f"input/{dir}/{dir}.json","w") as file:
                file.write(json_str)
            
                
            


if __name__ == "__main__":
    main()