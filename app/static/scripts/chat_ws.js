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
  const text = document.querySelector(`#message-${chunk.message_id} div`);
  text.textContent = chunk.text;
  text.scrollIntoView({ block: "center", behavior: "smooth" });
});

socket.on("new_message_done", (message) => {
  const bubble = document.getElementById(`message-${message.message_id}`);
  messageDone(bubble);

  bubble.classList.add("chat-loading-done");
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
