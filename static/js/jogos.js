(function () {
    'use strict';

    const grid = document.getElementById('gamesGrid');
    if (!grid) return;

    const searchInput = document.getElementById('catalogSearch');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const modal = document.getElementById('gameModal');
    const modalClose = document.getElementById('modalClose');
    const modalThumb = document.getElementById('modalThumb');
    const modalTitle = document.getElementById('modalTitle');
    const modalStores = document.getElementById('modalStores');
    const modalHeartBtn = document.getElementById('modalHeartBtn');
    const ratingRow = document.getElementById('ratingRow');

    const PAGE_SIZE = loadMoreBtn ? parseInt(loadMoreBtn.dataset.pageSize, 10) || 12 : 12;

    let termoAtual = '';
    let currentModalGameId = null;

    function cardHTML(jogo) {
        const thumbStyle = jogo.Thumb ? `style="background-image:url('${jogo.Thumb}'); background-size:cover;"` : '';
        const thumbFallback = jogo.Thumb ? '' : `<span>${(jogo.Title || '').slice(0, 4).toUpperCase()}</span>`;
        const metacritic = jogo.Metacritic_Score
            ? `<p style="margin:0; font-size:var(--fs-xs); color:var(--text-muted);">Metacritic: ${jogo.Metacritic_Score}</p>`
            : '';
        const heartActive = jogo.favoritado ? 'is-active' : '';

        return `
      <article class="news-card game-card" data-game-id="${jogo.Game_ID}" data-title="${jogo.Title}" data-thumb="${jogo.Thumb || ''}">
        <div class="news-thumb" ${thumbStyle}>
          ${thumbFallback}
          <button class="icon-btn wishlist-toggle ${heartActive}" aria-label="Favoritar ${jogo.Title}" data-heart>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s-7.5-4.6-10-9.1C.4 8.6 2 5 5.6 5c2 0 3.4 1 4.4 2.4C11 6 12.4 5 14.4 5 18 5 19.6 8.6 22 11.9 19.5 16.4 12 21 12 21z"/></svg>
          </button>
        </div>
        <div class="news-body">
          <h3>${jogo.Title}</h3>
          ${metacritic}
        </div>
      </article>
    `;
    }

    async function buscarJogos(offset) {
        const params = new URLSearchParams({ q: termoAtual, offset: offset });
        const resposta = await fetch(`/api/jogos?${params.toString()}`);
        return resposta.json();
    }

    async function toggleWishlist(gameId, titulo, thumb) {
        const resposta = await fetch('/api/wishlist/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_id: gameId, titulo: titulo, thumb: thumb }),
        });
        return resposta.json();
    }

    grid.addEventListener('click', async function (event) {
        const heartBtn = event.target.closest('[data-heart]');
        const card = event.target.closest('.game-card');
        if (!card) return;

        if (heartBtn) {
            event.stopPropagation();
            const { gameId, title, thumb } = card.dataset;
            const resultado = await toggleWishlist(gameId, title, thumb);
            heartBtn.classList.toggle('is-active', resultado.favoritado);
            return;
        }

        abrirModal(card.dataset.gameId);
    });

    if (searchInput) {
        let timeoutId;
        searchInput.addEventListener('input', function () {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(async function () {
                termoAtual = searchInput.value.trim();
                const jogos = await buscarJogos(0);

                grid.innerHTML = jogos.length
                    ? jogos.map(cardHTML).join('')
                    : '<p>Nenhum jogo encontrado com esse termo.</p>';

                loadMoreBtn.dataset.offset = jogos.length;
                loadMoreBtn.style.display = jogos.length < PAGE_SIZE ? 'none' : '';
            }, 350);
        });
    }

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', async function () {
            const offset = parseInt(loadMoreBtn.dataset.offset || '0', 10);
            const jogos = await buscarJogos(offset);

            grid.insertAdjacentHTML('beforeend', jogos.map(cardHTML).join(''));
            loadMoreBtn.dataset.offset = offset + jogos.length;

            if (jogos.length < PAGE_SIZE) {
                loadMoreBtn.style.display = 'none';
            }
        });
    }

    async function abrirModal(gameId) {
        currentModalGameId = gameId;
        const resposta = await fetch(`/api/jogos/${gameId}`);
        const dados = await resposta.json();
        const primeira = dados.ofertas[0] || {};

        modalTitle.textContent = primeira.Title || '';
        modalThumb.style.backgroundImage = primeira.Thumb ? `url('${primeira.Thumb}')` : '';
        modalThumb.style.backgroundSize = 'cover';
        modalThumb.style.backgroundPosition = 'center';

        modalStores.innerHTML = dados.ofertas.map(function (oferta) {
            const temDesconto = Number(oferta.Discount_Percent) > 0;
            const precos = temDesconto
                ? `<span class="price-old" style="margin-right:8px;">R$ ${Number(oferta.Normal_Price).toFixed(2)}</span><span class="price-new">R$ ${Number(oferta.Sale_Price).toFixed(2)}</span>`
                : `R$ ${Number(oferta.Sale_Price).toFixed(2)}`;

            return `
        <div class="modal-store-row">
          <span>${oferta.Store}</span>
          <span>${precos}</span>
        </div>
      `;
        }).join('') || '<p>Nenhuma oferta encontrada pra esse jogo ainda.</p>';

        modalHeartBtn.textContent = dados.favoritado ? 'Remover da lista de desejos' : 'Adicionar à lista de desejos';

        modal.classList.add('is-open');
    }

    function fecharModal() {
        modal.classList.remove('is-open');
        currentModalGameId = null;
    }

    if (modalClose) modalClose.addEventListener('click', fecharModal);
    if (modal) {
        modal.addEventListener('click', function (event) {
            if (event.target === modal) fecharModal();
        });
    }
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') fecharModal();
    });

    if (modalHeartBtn) {
        modalHeartBtn.addEventListener('click', async function () {
            if (!currentModalGameId) return;

            const card = grid.querySelector(`.game-card[data-game-id="${currentModalGameId}"]`);
            const titulo = modalTitle.textContent;
            const thumb = card ? card.dataset.thumb : '';
            const resultado = await toggleWishlist(currentModalGameId, titulo, thumb);

            modalHeartBtn.textContent = resultado.favoritado ? 'Remover da lista de desejos' : 'Adicionar à lista de desejos';

            if (card) {
                const heartBtn = card.querySelector('[data-heart]');
                if (heartBtn) heartBtn.classList.toggle('is-active', resultado.favoritado);
            }
        });
    }

    if (ratingRow) {
        ratingRow.addEventListener('click', function (event) {
            const btn = event.target.closest('button[data-rating]');
            if (!btn) return;
            ratingRow.querySelectorAll('button').forEach(function (b) { b.classList.remove('is-selected'); });
            btn.classList.add('is-selected');
        });
    }
})();