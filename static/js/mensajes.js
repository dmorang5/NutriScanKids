  document.addEventListener('DOMContentLoaded', () => {
    const messagesDiv = document.getElementById('messages');
    if (messagesDiv) {
      // Después de 4 segundos, oculta suavemente el div de mensajes
      setTimeout(() => {
        messagesDiv.style.transition = 'opacity 0.5s ease';
        messagesDiv.style.opacity = '0';
        setTimeout(() => {
          messagesDiv.style.display = 'none';
        }, 500);
      }, 4000);
    }
  });