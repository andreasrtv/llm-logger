const chatId = document.getElementById("chat-id").value;
const messageContainer = document.getElementById("message-container");
const socket = io.connect(window.location.origin);

function sendMessage() {
  const parent = document.querySelector("#message-container >div:last-child");
  const text = document.getElementById("message-input").value.trim();

  let parent_id = null;

  if (parent) {
    parent_id = parent.id.slice(8);
  }

  if (text) {
    socket.emit("send_message", {
      chat_id: chatId,
      sender: "user",
      text: text,
      parent_id: parent_id,
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
  if (
    message.parent_id &&
    !document.getElementById(`message-${message.parent_id}`)
  ) {
    return;
  }

  const bubble = document.createElement("div");
  bubble.id = `message-${message.id}`;
  bubble.classList.add(
    message.user_message ? "float-right" : "float-left",
    message.user_message ? "user-message" : "ai-message",
    "break-words",
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
  date.classList.add("text-sm", "text-slate-500");
  date.textContent = moment().calendar(message.created_at);

  const clickableId = document.createElement("a");
  clickableId.classList.add(
    "text-sm",
    "text-slate-500",
    "px-8",
    "hover:text-slate-300"
  );
  clickableId.href = `/chats/${chatId}?message_id=${message.id}`;
  clickableId.textContent = `${message.id}`;

  bubble.appendChild(text);
  bubble.appendChild(date);
  bubble.appendChild(clickableId);

  const messageChildren = document.createElement("input");
  messageChildren.classList.add("children");
  messageChildren.value = "[]";
  messageChildren.type = "hidden";

  const childrenIdxEl = document.createElement("input");
  childrenIdxEl.classList.add("current-child-idx");
  childrenIdxEl.value = "";
  childrenIdxEl.type = "hidden";

  bubble.appendChild(messageChildren);
  bubble.appendChild(childrenIdxEl);

  messageContainer.appendChild(bubble);

  if (!message.user_message) {
    addForkButtons(bubble, true);
  }

  if (message.parent_id) {
    const parentAIMessage = document.querySelector(
      `.ai-message#message-${message.parent_id}`
    );

    if (parentAIMessage) {
      updateForkPages(parentAIMessage, message.id);
    }
  }

  if (!message.stream) {
    messageDone(bubble);
  }
}

function messageDone(bubble) {
  bubble.classList.remove("chat-loading");

  const text = bubble.querySelector("span");
  text.classList.add("markdown-content");
  const escapedContent = text.textContent
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  text.innerHTML = DOMPurify.sanitize(marked.parse(escapedContent));

  document.querySelectorAll(`#${bubble.id} pre code`).forEach((el) => {
    addCopyButton(el);
    hljs.highlightElement(el);
  });

  bubble.scrollIntoView({ block: "center", behavior: "smooth" });
}

socket.emit("join", chatId);

socket.on("new_message", (message) => {
  newMessage(message);
});

socket.on("new_message_stream", (chunk) => {
  const text = document.querySelector(`#message-${chunk.message_id} span`);
  text.textContent += chunk.text;
  text.scrollIntoView({ block: "center", behavior: "smooth" });
});

socket.on("new_message_done", (message) => {
  const bubble = document.getElementById(`message-${message.message_id}`);
  messageDone(bubble);

  bubble.classList.add("chat-loading-done");
});
