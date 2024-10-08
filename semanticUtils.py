from typing import List
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModel
import outlines 

model_name = "numind/NuExtract-tiny"

# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)

model = outlines.models.transformers(model_name)

def build_classify_prompt(thing, classes):
    prompt = f"""Classify the given thing into one of the listed classes.
    {thing}
    Possible Classes:
    """
    for _class in classes:
        prompt += f"  - {_class}\n"

    prompt += """

    The most fittable classification is: """
    print("PROMPT:", prompt, "END")
    return prompt

# def classify(thing, classes: List[str]):
#     #tokenized_prompt = tokenizer(build_classify_prompt(thing, classes), return_tensors='pt').input_ids
#     tokenized_prompt = tokenizer.apply_chat_template([{
#         "role": "user", 
#         "content": build_classify_prompt(thing, classes)
#         }], tokenize=False, add_generation_prompt=True)
#
#     outputs = model.generate(
#             tokenizer([tokenized_prompt], return_tensors='pt').input_ids,
#             force_word_ids=tokenizer(classes, add_special_tokens=False).input_ids,
#             num_beams=5, # will this matter if i have a bajillion classes?
#             num_return_sequences=1,
#             no_repeat_ngram_size=1,
#             remove_invalid_values=True,    
#             )
#     print("OUTPUTS")
#     print(tokenizer.decode(outputs))
#

def classify(thing, classes):
    generator = outlines.generate.choice(model, classes)
    return generator(thing) #build_classify_prompt(thing, classes))

if __name__ == "__main__":
    print(classify("a dog", ["human", "animal"]))

    
    
