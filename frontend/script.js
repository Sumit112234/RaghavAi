async function sendMessage(event) {
    event.preventDefault();
    console.log("working");

    let userInput = document.getElementById("userInput").value;
    let chatBox = document.getElementById("chatBox");

    if (!userInput.trim()) return;

    chatBox.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;
    document.getElementById("userInput").value = "";

    try {
        let response = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: userInput }),
        });

        let data = await response.json();
        console.log(data)
        chatBox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
    } catch (error) {
        console.log(error)
        chatBox.innerHTML += `<p><strong>Error:</strong> Unable to connect to backend.</p>`;
    }
}

function hello(e){
    e.preventDefault();
    console.log("Hello");
}