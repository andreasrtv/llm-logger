const chatId = document.getElementById("chat-id").value;
const messageContainer = document.getElementById("message-container");
const socket = io.connect(window.location.origin);

function sendMessage() {
  const text = document.getElementById("message-input").value.trim();

  if (text) {
    const parent = document.querySelector("#message-container >div:last-child");

    socket.emit("send_message", {
      chat_id: chatId,
      sender: "user",
      text: text,
      parent_id: parent ? parent.id.slice(8) : null,
    });

    document.getElementById("message-input").value = "";
  }
}

socket.emit("join", chatId);

socket.on("new_message", (message) => {
  newMessage(message);
});

socket.on("new_message_stream", (chunk) => {
  const bubble = document.querySelector(`#message-${chunk.message_id} div`);
  formatMessage(bubble, chunk.text);
});

socket.on("new_message_done", (message) => {
  const bubble = document.getElementById(`message-${message.message_id}`);
  messageDone(bubble);
  bubble.classList.add("chat-loading-done");
});

socket.on("error", (error) => {
  if (error.message_id) {
    const bubble = document.getElementById(`message-${error.message_id}`);
    bubble.classList.remove("chat-loading");
    bubble.classList.add("chat-error");
    bubble.querySelector("div").innerText += error.error;
    bubble.querySelector("hr").remove();
    bubble.querySelector("span").remove();
    bubble.querySelector("a").remove();
    bubble.scrollIntoView({ block: "center", behavior: "smooth" });
  } else {
    const errorBubble = document.createElement("div");
    errorBubble.classList.add("chat-error");
    errorBubble.classList.add(
      "float-left",
      "ai-message",
      "mb-4",
      "w-2/3",
      "p-4",
      "rounded-2xl",
      "relative",
      "chat-error",
      "text-white"
    );
    errorBubble.innerText = error.error;
    messageContainer.appendChild(errorBubble);
    errorBubble.scrollIntoView({ block: "center", behavior: "smooth" });
  }
});

document.getElementById("message-form").onsubmit = (e) => {
  e.preventDefault();
  sendMessage();
};

document.getElementById("message-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
