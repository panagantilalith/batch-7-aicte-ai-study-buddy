function toggleAnswer(btn) {
    const ans = btn.nextElementSibling;
    if (ans.style.display === "block") {
        ans.style.display = "none";
        btn.innerText = "Show Answer";
    } else {
        ans.style.display = "block";
        btn.innerText = "Hide Answer";
    }
}
async function sendChat() {
    const input = document.getElementById("chatInput");
    const responseBox = document.getElementById("chatResponse");

    if (!input.value.trim()) return;

    responseBox.innerHTML = "Thinking... ⏳";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: input.value})
        });

        const data = await res.json();

        // 🔹 Clean markdown symbols
        let cleanText = data.reply
            .replace(/\*\*/g, "")
            .replace(/###/g, "")
            .replace(/\*/g, "•");

        // 🔹 Split into readable lines
        let formatted = cleanText.split("\n").map(line => {
            return `<p>${line}</p>`;
        }).join("");

        responseBox.innerHTML = formatted;
        input.value = "";

    } catch (err) {
        responseBox.innerHTML = "Error getting response.";
    }
}