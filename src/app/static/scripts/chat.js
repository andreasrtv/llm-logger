const copySVG = `<svg width="24px" height="24px" viewBox="0 0 24 24" fill="#ffffff" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M21 8C21 6.34315 19.6569 5 18 5H10C8.34315 5 7 6.34315 7 8V20C7 21.6569 8.34315 23 10 23H18C19.6569 23 21 21.6569 21 20V8ZM19 8C19 7.44772 18.5523 7 18 7H10C9.44772 7 9 7.44772 9 8V20C9 20.5523 9.44772 21 10 21H18C18.5523 21 19 20.5523 19 20V8Z" fill="#ffffff"/><path d="M6 3H16C16.5523 3 17 2.55228 17 2C17 1.44772 16.5523 1 16 1H6C4.34315 1 3 2.34315 3 4V18C3 18.5523 3.44772 19 4 19C4.55228 19 5 18.5523 5 18V4C5 3.44772 5.44772 3 6 3Z"/></svg>`;
const forkSVG = `<svg width="24px" height="24px" fill="#ffffff" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 33.627 33.628"xml:space="preserve"><g><path d="M27.131,8.383c0-2.092-1.701-3.794-3.794-3.794s-3.793,1.702-3.793,3.794c0,0.99,0.39,1.885,1.013,2.561c-0.474,2.004-1.639,2.393-4.167,3.029c-1.279,0.322-2.753,0.7-4.099,1.501V7.003c1.072-0.671,1.793-1.854,1.793-3.209C14.084,1.702,12.382,0,10.292,0C8.199,0,6.497,1.702,6.497,3.794c0,1.356,0.722,2.539,1.795,3.21v19.62c-1.073,0.671-1.795,1.854-1.795,3.21c0,2.092,1.702,3.794,3.795,3.794c2.092,0,3.793-1.702,3.793-3.794c0-1.355-0.722-2.539-1.793-3.209v-3.846c0.496-3.768,2.321-4.232,5.075-4.926c2.527-0.637,5.955-1.513,7.048-5.852C25.981,11.535,27.131,10.099,27.131,8.383z M10.292,2.002c0.988,0,1.793,0.805,1.793,1.794c0,0.989-0.806,1.793-1.793,1.793c-0.989,0-1.795-0.805-1.795-1.793C8.498,2.806,9.302,2.002,10.292,2.002z M10.292,31.627c-0.989,0-1.795-0.807-1.795-1.794c0-0.989,0.806-1.793,1.795-1.793c0.988,0,1.793,0.806,1.793,1.793C12.085,30.824,11.28,31.627,10.292,31.627z M23.337,10.177c-0.989,0-1.793-0.805-1.793-1.793c0-0.989,0.806-1.794,1.793-1.794c0.988,0,1.794,0.805,1.794,1.794C25.131,9.373,24.327,10.177,23.337,10.177z"/></g></svg>`;
const arrowLeftSVG = `<svg fill=" #ffffff" width="12px" height="12px" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"> <path d="M23.505 0c0.271 0 0.549 0.107 0.757 0.316 0.417 0.417 0.417 1.098 0 1.515l-14.258 14.264 14.050 14.050c0.417 0.417 0.417 1.098 0 1.515s-1.098 0.417-1.515 0l-14.807-14.807c-0.417-0.417-0.417-1.098 0-1.515l15.015-15.022c0.208-0.208 0.486-0.316 0.757-0.316z"> </path> </svg>`;
const arrowRightSVG = `<svg fill=" #ffffff" width="12px" height="12px" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg"> <path d="M8.489 31.975c-0.271 0-0.549-0.107-0.757-0.316-0.417-0.417-0.417-1.098 0-1.515l14.258-14.264-14.050-14.050c-0.417-0.417-0.417-1.098 0-1.515s1.098-0.417 1.515 0l14.807 14.807c0.417 0.417 0.417 1.098 0 1.515l-15.015 15.022c-0.208 0.208-0.486 0.316-0.757 0.316z"> </path></svg>`;

function addCopyButton(codeBlock) {
  const button = document.createElement("button");
  button.classList.add("copy-btn");
  button.innerHTML = copySVG;

  const preBlock = codeBlock.parentNode;
  preBlock.style.position = "relative";
  preBlock.appendChild(button);

  button.addEventListener("click", () => {
    const codeText = codeBlock.textContent || codeBlock.innerText;

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard
        .writeText(codeText)
        .then(() => {})
        .catch(() => {});
    } else {
      const textArea = document.createElement("textarea");
      textArea.value = codeText;

      textArea.style.position = "absolute";
      textArea.style.left = "-999999px";

      document.body.prepend(textArea);
      textArea.select();

      try {
        document.execCommand("copy");
      } catch (error) {
        console.error(error);
      } finally {
        textArea.remove();
      }
    }
  });
}

function newFork(event) {
  const bubble = event.currentTarget.parentNode;

  const messages = [...document.querySelectorAll("#message-container .message")];
  const forkIdx = messages.findIndex((el) => el === bubble);

  if (forkIdx !== messages.length - 1) {
    for (let i = messages.length - 1; i > forkIdx; i--) {
      messages[i].remove();
    }

    const forkPages = bubble.querySelector(".fork-pages");

    const text = forkPages.querySelector("span");
    const lastPage = parseInt(text.textContent.split("/")[1]) + 1;
    text.textContent = `${lastPage}/${lastPage}`;

    const childrenIds = JSON.parse(bubble.querySelector(".children").value);
    const arrows = forkPages.querySelectorAll("a");

    arrows[0].href = `${arrows[0].href.split("?")[0]}?message_id=${childrenIds[childrenIds.length - 1]}`;
    arrows[1].href = `${arrows[1].href.split("?")[0]}?message_id=${childrenIds[0]}`;

    forkPages.style.display = "flex";
    bubble.scrollIntoView({ block: "end", behavior: "smooth" });
  }
}

function addForkButton(bubble) {
  const forkButton = document.createElement("button");
  forkButton.classList.add("fork-btn");
  forkButton.style.display = "none";
  forkButton.innerHTML = forkSVG;
  bubble.appendChild(forkButton);

  forkButton.addEventListener("click", newFork);
}

function addForkPages(bubble) {
  const forkPages = document.createElement("div");
  forkPages.classList.add("fork-pages");
  bubble.appendChild(forkPages);

  const backArrow = document.createElement("a");
  backArrow.innerHTML = arrowLeftSVG;
  backArrow.classList.add("fork-arrows");
  forkPages.appendChild(backArrow);

  const text = document.createElement("span");
  text.style.color = "#ffffff";
  forkPages.appendChild(text);

  const forwardArrow = document.createElement("a");
  forwardArrow.innerHTML = arrowRightSVG;
  forwardArrow.classList.add("fork-arrows");
  forkPages.appendChild(forwardArrow);

  updateForkPages(bubble);
}

function updateForkPages(bubble, newChild = null) {
  const forkPages = bubble.querySelector(".fork-pages");
  const backArrow = forkPages.querySelector("a");
  const text = forkPages.querySelector("span");
  const forwardArrow = forkPages.querySelectorAll("a")[1];

  const messageChildren = bubble.querySelector(".children");
  const messageChildrenIdx = bubble.querySelector(".current-child-idx");

  let childrenIds = JSON.parse(messageChildren.value);
  let currChildIdx = parseInt(messageChildrenIdx.value);

  if (newChild) {
    childrenIds.push(newChild);
    messageChildren.value = JSON.stringify(childrenIds);

    currChildIdx = childrenIds.length - 1;
    messageChildrenIdx.value = currChildIdx;
  }

  if (childrenIds.length != 0) {
    bubble.querySelector(".fork-btn").style.display = "inline-block";
  }

  if (isNaN(currChildIdx) || childrenIds.length <= 1) {
    forkPages.style.display = "none";
  } else {
    forkPages.style.display = "flex";
  }

  const hrefBase = `${window.location.pathname}?message_id=`;
  const previousFork = childrenIds[(childrenIds.length + currChildIdx - 1) % childrenIds.length];
  const nextFork = childrenIds[(currChildIdx + 1) % childrenIds.length];

  backArrow.href = hrefBase + previousFork;
  text.textContent = `${currChildIdx + 1}/${childrenIds.length}`;
  forwardArrow.href = hrefBase + nextFork;
}

function formatMessage(textEl, rawText = null) {
  let prettyContent = (rawText ? rawText : textEl.textContent).replace(/</g, "&lt;").replace(/>/g, "&gt;");
  textEl.innerHTML = DOMPurify.sanitize(marked.parse(prettyContent));
}

function messageDone(bubble, scroll = true) {
  bubble.classList.remove("chat-loading");

  document.querySelectorAll(`#${bubble.id} pre code`).forEach((el) => {
    el.textContent = el.textContent.replace(/&lt;/g, "<").replace(/&gt;/g, ">");
    addCopyButton(el);
    hljs.highlightElement(el);
  });

  if (scroll) {
    bubble.scrollIntoView({ behavior: "smooth" });
  }
}

function newMessage(message) {
  if (message.parent_id && !document.getElementById(`message-${message.parent_id}`)) {
    return;
  }

  const bubble = document.createElement("div");
  bubble.id = `message-${message.id}`;
  bubble.classList.add("message", ...(message.user_message ? ["user-message"] : ["ai-message", "chat-loading"]));

  const text = document.createElement("div");
  text.classList.add("message-text", "markdown-content");
  text.textContent = message.text;

  const hr = document.createElement("hr");
  hr.classList.add("divider", "message-divider");

  const date = document.createElement("span");
  date.classList.add("message-footer");
  date.textContent = moment().calendar(message.created_at);

  const clickableId = document.createElement("a");
  clickableId.classList.add("message-footer", "message-footer-clickable");
  clickableId.href = `${window.location.pathname}?message_id=${message.id}`;
  clickableId.textContent = `${message.id}`;

  const modifyButton = document.createElement("button");
  modifyButton.classList.add("message-footer", "message-footer-clickable");

  if (message.user_message) {
    modifyButton.classList.add("delete-btn");
    modifyButton.textContent = "Delete";
    modifyButton.addEventListener("click", () => {
      deleteMessage(message.id);
    });
  } else {
    document.querySelectorAll(".reprompt-btn").forEach((el) => {
      el.remove();
    });

    modifyButton.classList.add("reprompt-btn");
    modifyButton.textContent = "Reprompt";
    modifyButton.addEventListener("click", () => {
      repromptMessage(message.id);
    });
  }

  bubble.appendChild(text);
  bubble.appendChild(hr);
  bubble.appendChild(date);
  bubble.appendChild(clickableId);
  bubble.appendChild(modifyButton);

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
    addForkButton(bubble);
    addForkPages(bubble);
  }

  if (message.parent_id) {
    const parentAIMessage = document.querySelector(`.ai-message#message-${message.parent_id}`);

    if (parentAIMessage) {
      updateForkPages(parentAIMessage, message.id);
    }
  }

  if (!message.stream) {
    formatMessage(text);
    messageDone(bubble);
  }

  bubble.scrollIntoView({ behavior: "smooth" });
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".ai-message").forEach((el) => {
    if (document.querySelector("#message-form")) {
      addForkButton(el);
    }
    addForkPages(el);
  });

  document.querySelectorAll("#message-container .message").forEach((bubble) => {
    formatMessage(bubble.querySelector(".message-text"));
    messageDone(bubble, false);
  });

  const messageId = new URLSearchParams(window.location.search).get("message_id");

  if (messageId) {
    const bubble = document.getElementById(`message-${messageId}`);
    if (bubble) {
      bubble.scrollIntoView();
      bubble.classList.add("chat-highlight");
    }
  }
});
