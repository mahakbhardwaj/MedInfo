const chatForm = document.querySelector("#chat-form");
const chatMessages = document.querySelector("#chat-messages");
const chatQuestion = document.querySelector("#chat-question");
const chatStatus = document.querySelector("#chat-status");
const chatLoading = document.querySelector("#chat-loading");
const clearChatButton = document.querySelector("#clear-chat");
const chatbotPage = document.querySelector(".chat-page");

function addMessage(text, messageType) {
    const message = document.createElement("div");
    message.className = `message ${messageType}-message`;
    const label = document.createElement("span");
    label.className = "message-label";
    label.textContent = messageType === "user" ? "You" : "MedInfo assistant";
    const paragraph = document.createElement("p");
    paragraph.textContent = text;
    message.append(label, paragraph);
    chatMessages.appendChild(message);
    message.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

if (chatForm) {
    chatForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const question = chatQuestion.value.trim();

        if (!question) {
            chatStatus.textContent = "Please enter a question.";
            return;
        }

        addMessage(question, "user");
        chatQuestion.value = "";
        chatLoading.hidden = false;
        chatLoading.textContent = "Preparing your answer...";
        chatStatus.textContent = "";
        chatForm.querySelector("button[type='submit']").disabled = true;

        const medicineId = chatbotPage.dataset.medicineId;
        const requestBody = { message: question };
        if (medicineId) {
            requestBody.medicine_id = Number(medicineId);
        }

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestBody),
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.answer || "The question could not be processed.");
            }
            addMessage(data.answer, "bot");
        } catch (error) {
            chatStatus.textContent = error.message || "Unable to contact the chatbot. Please try again.";
        } finally {
            chatLoading.hidden = true;
            chatForm.querySelector("button[type='submit']").disabled = false;
        }
    });
}

if (clearChatButton) {
    clearChatButton.addEventListener("click", () => {
        chatMessages.innerHTML = "";
        chatStatus.textContent = "Conversation cleared.";
        chatQuestion.focus();
    });
}
