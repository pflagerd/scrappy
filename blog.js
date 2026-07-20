document.addEventListener("DOMContentLoaded", () => {
    const articles = document.querySelectorAll("article");

    articles.forEach((article, index) => {
        const articleId = article.id || `article-${index}`;
        article.id = articleId;

        const contentChildren = Array.from(article.children);

        if (contentChildren.length < 1) return;

        // Inject toggle span into first child
        const toggleSpan = document.createElement("span");
        toggleSpan.className = "toggle-control";
        contentChildren[0].appendChild(toggleSpan);

        const getHeightForFirstN = (n) => {
            article.style.height = 'auto';
            void article.offsetHeight;

            let total = 0;
            for (let i = 0; i < Math.min(n, contentChildren.length); i++) {
                const el = contentChildren[i];
                const style = getComputedStyle(el);
                total += el.offsetHeight + parseFloat(style.marginTop) + parseFloat(style.marginBottom);
            }
            return total + parseFloat(getComputedStyle(document.body).fontSize); // Add 1 em of body for artificial final margin.
        };

        const getFullHeight = () => {
            article.style.height = 'auto';
            void article.offsetHeight;

            let height = contentChildren.reduce((acc, el) => {
                const style = getComputedStyle(el);
                return acc + el.offsetHeight + parseFloat(style.marginTop) + parseFloat(style.marginBottom);
            }, 0);
            height += parseFloat(getComputedStyle(document.body).fontSize); // Add 1 em of body for artificial final margin.
            return height;
        };

        const storedState = localStorage.getItem(articleId);
        let isCollapsed;

        if (storedState === null) {
            // First-time load: collapse all except the first article
            isCollapsed = index !== 0;
        } else {
            isCollapsed = storedState === "collapsed";
        }

        const applyState = (collapsed) => {
            const targetHeight = collapsed ? getHeightForFirstN(3) : getFullHeight();
            article.style.height = targetHeight + "px";
            toggleSpan.textContent = collapsed ? "Expand ▼" : "Collapse ▲";
            localStorage.setItem(articleId, collapsed ? "collapsed" : "expanded");

            if (!collapsed) {
                article.addEventListener('transitionend', () => {
                    article.style.height = 'auto';
                }, {once: true});
            }
        };

        applyState(isCollapsed);

        toggleSpan.addEventListener("click", () => {
            const collapsed = toggleSpan.textContent.includes("Expand");
            article.style.height = article.offsetHeight + 'px';
            requestAnimationFrame(() => {
                applyState(!collapsed);
            });
        });
    });
});
