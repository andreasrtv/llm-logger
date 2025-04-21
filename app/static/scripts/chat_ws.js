const chatId = document.getElementById("chat-id").value;
const messageContainer = document.getElementById("message-container");
const socket = io.connect(window.location.origin);

function sendMessage() {
  const text = document.getElementById("message-input").value.trim();

  if (text) {
    const parent = document.querySelector("#message-container .message:last-child");

    socket.emit("send_message", {
      chat_id: chatId,
      sender: "user",
      text: text,
      parent_id: parent ? parent.id.slice(8) : null,
    });

    document.getElementById("message-input").value = "";
  }
}

function deleteMessage(messageId) {
  const messageText = document.querySelector(`#message-${messageId} .message-text`).textContent;
  if (
    confirm(`Are you sure? Only do this if you made an input mistake. Message:\n\n> ${messageText.substring(0, 100)}`)
  ) {
    socket.emit("delete_message", {
      chat_id: chatId,
      message_id: messageId,
    });
  }
}

function repromptMessage(messageId) {
  const messageText = document.querySelector(`#message-${messageId} .message-text`).textContent;
  if (confirm(`Are you sure? Message:\n\n> ${messageText.substring(0, 100)}`)) {
    socket.emit("reprompt_message", {
      chat_id: chatId,
      message_id: messageId,
    });
  }
}

socket.emit("join", chatId);

socket.on("new_message", (message) => {
  newMessage(message);
});

socket.on("new_message_stream", (chunk) => {
  const textEl = document.querySelector(`#message-${chunk.message_id} .message-text`);

  if (textEl) {
    formatMessage(textEl, chunk.text);
  }
});

socket.on("new_message_done", (message) => {
  const bubble = document.getElementById(`message-${message.message_id}`);

  if (bubble) {
    messageDone(bubble);
    bubble.classList.add("chat-loading-done");
  }
});

socket.on("error", (error) => {
  if (error.message_id) {
    const bubble = document.getElementById(`message-${error.message_id}`);
    bubble.classList.remove("chat-loading");
    bubble.classList.add("chat-error");
    bubble.querySelector(".message-text").innerText += error.error;

    bubble.querySelectorAll(":not(.message-text)").forEach((el) => {
      el.remove();
    });

    bubble.scrollIntoView({ behavior: "smooth" });
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
    errorBubble.scrollIntoView({ behavior: "smooth" });
  }
});

socket.on("delete_message", (message) => {
  const messages = [...document.querySelectorAll("#message-container >div")];
  const messageIdx = messages.findIndex((el) => el.id === `message-${message.message_id}`);

  for (let i = messages.length - 1; i >= messageIdx; i--) {
    messages[i].remove();
  }
});

document.getElementById("message-form").onsubmit = (e) => {
  e.preventDefault();
  sendMessage();
};
