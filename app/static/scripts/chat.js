const chatId = document.getElementById("chat-id").value;
const socket = io.connect(window.location.origin);

socket.emit("join", chatId);

const sendMessage = () => {
  const text = document.getElementById("message-input").value;

  if (text.trim()) {
    socket.emit("send_message", {
      chat_id: chatId,
      sender: "user",
      text: text,
    });

    document.getElementById("message-input").value = "";
  }
};

socket.on("new_message", (message) => {
  const bubbleEl = document.createElement("div");
  bubbleEl.id = `message-${message.id}`;
  bubbleEl.classList.add(
    message.user_message ? "float-right" : "float-left",
    "mb-4",
    "w-2/3",
    "bg-zinc-700",
    "p-4",
    "rounded-2xl",
    "chat-loading"
  );

  const textEl = document.createElement("p");
  textEl.classList.add("text-white", "whitespace-pre-wrap");

  if (message.stream) {
    textEl.textContent = message.text;
  } else {
    bubbleEl.classList.remove("chat-loading");
    textEl.classList.add("markdown-content");
    textEl.innerHTML = DOMPurify.sanitize(marked.parse(message.text));
  }

  const dateEl = document.createElement("span");
  dateEl.classList.add("text-xs", "text-slate-500");
  dateEl.textContent = message.created_at;

  bubbleEl.appendChild(textEl);
  bubbleEl.appendChild(dateEl);
  messageContainer.appendChild(bubbleEl);

  messageContainer.scrollTop = messageContainer.scrollHeight;
});

socket.on("new_message_stream", (chunk) => {
  const bubbleEl = document.getElementById(`message-${chunk.message_id}`);
  const textEl = bubbleEl.querySelector("p");

  textEl.textContent += chunk.text;

  messageContainer.scrollTop = messageContainer.scrollHeight;
});

socket.on("new_message_done", (message) => {
  const bubbleEl = document.getElementById(`message-${message.message_id}`);
  bubbleEl.classList.remove("chat-loading");

  const textEl = bubbleEl.querySelector("p");
  textEl.classList.add("markdown-content");
  textEl.innerHTML = DOMPurify.sanitize(marked.parse(textEl.textContent));

  messageContainer.scrollTop = messageContainer.scrollHeight;
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

function addCopyButtons() {
  const codeBlocks = document.querySelectorAll("pre code");

  codeBlocks.forEach((codeBlock) => {
    const button = document.createElement("button");
    button.classList.add("copy-btn");
    button.textContent = "Copy";

    const preBlock = codeBlock.parentNode;
    preBlock.style.position = "relative";
    preBlock.appendChild(button);

    button.addEventListener("click", () => {
      const codeText = codeBlock.textContent || codeBlock.innerText;
      navigator.clipboard
        .writeText(codeText)
        .then(() => {})
        .catch(() => {});
    });
  });
}

addCopyButtons();
