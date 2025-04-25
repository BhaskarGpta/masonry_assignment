import os
from dataclasses import dataclass, field

prompts = {}

prompt_dir = os.path.join(os.path.dirname(__file__), "prompts") #Load prompts from directory
for filename in os.listdir(prompt_dir):
    if filename.endswith(".txt"):
        attribute_name = os.path.splitext(filename)[0] 
        with open(os.path.join(prompt_dir, filename), "r") as file:
            prompts[attribute_name] = file.read()
            
@dataclass
class Prompts:
    pass

for key, value in prompts.items():
    setattr(Prompts, key, value)
    
