"""
Shader Agent Trainer
- Fine-tunes a T5 seq2seq model on prompt -> shader code pairs.
- Expected dataset: JSONL lines with {"prompt": "...", "code": "..."}
- Credits: Uses modelling approach compatible with HuggingFace Transformers.
- External repos referenced for inspiration/format: ShaderGen (MIT), shd_sokol (MIT).
- Verify and comply with those repos' LICENSE files before redistribution.
"""

from pathlib import Path
import argparse
import json
import random
from datasets import load_dataset, Dataset
from transformers import T5ForConditionalGeneration, T5TokenizerFast, Trainer, TrainingArguments, DataCollatorForSeq2Seq

def load_jsonl_dataset(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if "prompt" in data and "code" in data:
                items.append({"prompt": data["prompt"], "code": data["code"]})
    return Dataset.from_list(items)

def preprocess(batch, tokenizer, max_input_len=256, max_target_len=1024):
    inputs = ["generate shader: " + p for p in batch["prompt"]]
    model_inputs = tokenizer(inputs, truncation=True, padding="max_length", max_length=max_input_len)
    labels = tokenizer(batch["code"], truncation=True, padding="max_length", max_length=max_target_len).input_ids
    model_inputs["labels"] = labels
    return model_inputs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-file", required=True, help="JSONL file with prompt/code pairs")
    parser.add_argument("--output-dir", default="checkpoints/shader_agent")
    parser.add_argument("--model", default="t5-small")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()

    tokenizer = T5TokenizerFast.from_pretrained(args.model)
    model = T5ForConditionalGeneration.from_pretrained(args.model)

    ds = load_jsonl_dataset(args.train_file)
    ds = ds.train_test_split(test_size=0.05)

    def token_fn(batch): return preprocess(batch, tokenizer)
    tokenized_train = ds["train"].map(lambda b: preprocess(b, tokenizer), batched=True, remove_columns=["prompt","code"])
    tokenized_val = ds["test"].map(lambda b: preprocess(b, tokenizer), batched=True, remove_columns=["prompt","code"])

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        predict_with_generate=True,
        evaluation_strategy="steps",
        eval_steps=200,
        logging_steps=100,
        save_steps=500,
        num_train_epochs=args.epochs,
        fp16=False,
        push_to_hub=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
        data_collator=data_collator,
        tokenizer=tokenizer
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Training complete. Model saved to", args.output_dir)

if __name__ == "__main__":
    main()
