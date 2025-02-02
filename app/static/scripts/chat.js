const chatId = document.getElementById("chat-id").value;
const messageContainer = document.getElementById("message-container");
const socket = io.connect(window.location.origin);

function sendMessage() {
  const text = document.getElementById("message-input").value;

  if (text.trim()) {
    socket.emit("send_message", {
      chat_id: chatId,
      sender: "user",
      text: text,
    });

    document.getElementById("message-input").value = "";
  }
}

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

function newMessage(message) {
  const bubble = document.createElement("div");
  bubble.id = `message-${message.id}`;
  bubble.classList.add(
    message.user_message ? "float-right" : "float-left",
    "mb-4",
    "w-2/3",
    "bg-zinc-700",
    "p-4",
    "rounded-2xl",
    "chat-loading",
    "relative"
  );

  const text = document.createElement("span");
  text.classList.add("text-white", "whitespace-pre-wrap");
  text.textContent = message.text;

  const date = document.createElement("span");
  date.classList.add("text-xs", "text-slate-500");
  date.textContent = message.created_at;

  bubble.appendChild(text);
  bubble.appendChild(date);
  messageContainer.appendChild(bubble);

  if (!message.stream) {
    messageDone(bubble);
  }
}

function messageDone(bubble) {
  bubble.classList.remove("chat-loading");

  const text = bubble.querySelector("span");
  text.classList.add("markdown-content");
  text.innerHTML = DOMPurify.sanitize(marked.parse(text.textContent));

  document.querySelectorAll(`#${bubble.id} pre code`).forEach((el) => {
    addCopyButton(el);
    hljs.highlightElement(el);
  });
}

socket.emit("join", chatId);

socket.on("new_message", (message) => {
  newMessage(message);

  messageContainer.scrollTop = messageContainer.scrollHeight;
});

socket.on("new_message_stream", (chunk) => {
  const text = document.querySelector(`#message-${chunk.message_id} span`);
  text.textContent += chunk.text;

  messageContainer.scrollTop = messageContainer.scrollHeight;
});

socket.on("new_message_done", (message) => {
  const bubble = document.getElementById(`message-${message.message_id}`);
  messageDone(bubble);

  messageContainer.scrollTop = messageContainer.scrollHeight;
  bubble.classList.add("chat-loading-done");
});
