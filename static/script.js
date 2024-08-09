function openModal() {
    const modal = document.getElementById('modal-container');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'modal-container' || e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}



function deletar() {
    const modal = document.getElementById('modal-delete');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'modal-delete' || e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}


function openTag() {
    const modal = document.getElementById('modal-tag');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'modal-tag' || e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}


function opencolab() {
    const modal = document.getElementById('modal-colab');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'modal-colab' || e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}


function opencolab_per() {
    const modal = document.getElementById('modal-colab_per');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'modal-colab_per' || e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}



function notificacao() {
   const modal = document.getElementById('modal-mensagem');
   modal.classList.add('mostrar');
  modal.addEventListener('click', (e) => {
       if (e.target.id === 'modal-mensagem' || e.target.id === 'fechar') {
           modal.classList.remove('mostrar');
       }
   });
}

function open_ideia() {
    const modal = document.getElementById('modal-ideia');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'modal-ideia' || e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}

function carregamento() {
    const idea = document.getElementById('idea_chat').value;

    if (idea.trim() === '') {
        alert('Por favor, preencha o campo "Ideia" antes de continuar.');
        return;
    }

    const modal = document.getElementById('modal-carregar');
    const modal_fechar = document.getElementById('modal-container');
    modal_fechar.classList.remove('mostrar');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}

function confirmacao() {
    const modal = document.getElementById('modal-confirm');
    modal.classList.add('mostrar');
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'modal-confirm' || e.target.id === 'fechar') {
            modal.classList.remove('mostrar');
        }
    });
}

