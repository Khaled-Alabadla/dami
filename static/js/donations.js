async function commitToDonate(requestId) {
  const btn = document.querySelector(
    `[data-request-id="${requestId}"] .btn-commit`,
  );
  btn.disabled = true;
  btn.textContent = "جاري التسجيل...";

  try {
    const response = await fetch(`/donate/commit/${requestId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();

    if (data.success) {
      btn.textContent = "✅ أنت ملتزم بهذه الحالة";
      btn.classList.add("btn-committed");
      showToast("شكراً! تم تسجيل التزامك بنجاح.", "success");

      // Block all other uncommitted donate buttons on the page
      document.querySelectorAll(".btn-commit:not(.btn-committed):not(.btn-completed)").forEach((otherBtn) => {
        otherBtn.disabled = true;
        otherBtn.classList.add("btn-blocked");
        otherBtn.textContent = "⏳ لديك التزام قائم بحالة أخرى";
      });
    } else {
      btn.disabled = false;
      btn.innerHTML = `أنا قادم للتبرع <img width="35px" src="/static/images/blood.webp" alt="" />`;

      if (data.days_remaining) {
        showToast(
          `غير مؤهل حالياً. يمكنك التبرع بعد ${data.days_remaining} يوماً.`,
          "warning",
        );
      } else if (data.already_committed_elsewhere) {
        showToast(data.error, "warning");
      } else {
        showToast(data.error, "error");
      }
    }
  } catch (err) {
    btn.disabled = false;
    btn.innerHTML = `أنا قادم للتبرع <img width="35px" src="/static/images/blood.webp" alt="" />`;
    showToast("حدث خطأ في الاتصال، حاول مجدداً.", "error");
  }
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4500);
}
