"""Gradio web UI for The Unofficial Guide.

    python app.py    ->  open http://localhost:7860

Enter a question about a UC Berkeley CS professor/course; get a grounded answer with the
reviews it cited, plus the raw retrieved chunks (so the grounding is visible in the demo).
"""
import gradio as gr

from generate import answer

EXAMPLES = [
    "What do students say about Dan Garcia for CS61A?",
    "Are John Canny's classes worth taking?",
    "Which professor gives good feedback and is patient in office hours?",
    "Is CS61B hard, and who teaches it well?",
    "Which Berkeley CS or data science professors should I avoid?",
    "What's the best dorm for freshmen at Berkeley?",
]


def handle_query(question: str):
    if not question or not question.strip():
        return "Type a question above.", "", ""
    r = answer(question)

    sources = "\n".join(f"• {s}" for s in r["sources"]) or "(no in-domain sources — declined)"

    # Show the actual retrieved chunks so viewers can see the answer is grounded.
    retrieved = "\n\n".join(
        f"[{i}] {c['professor']} ({c['course']})  |  distance {c['distance']}\n{c['text']}"
        for i, c in enumerate(r["contexts"], 1)
    )
    return r["answer"], sources, retrieved


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# 🐻 The Unofficial Guide\n"
        "Ask about **UC Berkeley CS professors & courses**. Answers are grounded in real "
        "student reviews and cite their sources — the system declines questions the reviews "
        "don't cover."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. Which professor should I take for CS61A?")
    btn = gr.Button("Ask", variant="primary")
    answer_box = gr.Textbox(label="Answer", lines=8)
    sources_box = gr.Textbox(label="Sources (cited from)", lines=4)
    retrieved_box = gr.Textbox(label="Retrieved reviews (the grounding context)", lines=12)
    gr.Examples(EXAMPLES, inputs=inp)

    outputs = [answer_box, sources_box, retrieved_box]
    btn.click(handle_query, inputs=inp, outputs=outputs)
    inp.submit(handle_query, inputs=inp, outputs=outputs)


if __name__ == "__main__":
    demo.launch()
