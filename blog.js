"use strict";

/*
 * Collapsible <article> elements with persisted state.
 *
 * Design rule: an EXPANDED article has NO inline height (it falls back to the
 * stylesheet, i.e. height:auto), so late-loading images/videos/iframes, web
 * fonts and window resizes can never clip it. A pixel height exists only
 * (a) while collapsed and (b) for the duration of an expand animation.
 *
 * CSS this expects on <article>:  overflow: hidden;  transition: height <dur>;
 */
document.addEventListener("DOMContentLoaded", () => {
    const COLLAPSED_FALLBACK_COUNT = 3;   // used only if no child has a `meta` attribute

    document.querySelectorAll("article").forEach((article, index) => {
        const articleId = article.id || `article-${index}`;
        article.id = articleId;

        const children = Array.from(article.children);
        if (children.length < 1) return;

        // Inject toggle span into first child
        const toggleSpan = document.createElement("span");
        toggleSpan.className = "toggle-control";
        children[0].appendChild(toggleSpan);

        // Last child that stays visible when collapsed: the last child carrying
        // a `meta` attribute, otherwise the Nth child (original behaviour).
        const metaChildren = children.filter((el) => el.hasAttribute("meta"));
        const lastVisible = metaChildren.length
            ? metaChildren[metaChildren.length - 1]
            : children[Math.min(COLLAPSED_FALLBACK_COUNT, children.length) - 1];

        // ---- measurement helpers -------------------------------------------

        const px = (v) => parseFloat(v) || 0;
        const oneEm = () => px(getComputedStyle(document.body).fontSize);

        const boxInfo = () => {
            const cs = getComputedStyle(article);
            return {
                borderBox: cs.boxSizing === "border-box",
                padT: px(cs.paddingTop),     padB: px(cs.paddingBottom),
                borT: px(cs.borderTopWidth), borB: px(cs.borderBottomWidth),
            };
        };

        // Rendered border-box height -> value suitable for style.height
        const currentStyleHeight = () => {
            const b = boxInfo();
            const h = article.getBoundingClientRect().height;
            return b.borderBox ? h : h - b.padT - b.padB - b.borT - b.borB;
        };

        // Height that shows everything down to the bottom of `lastVisible`.
        // Measured from actual rendered positions, so margin collapsing,
        // nested margins, padding and borders are all accounted for.
        const collapsedHeight = () => {
            const b = boxInfo();
            const span = lastVisible.getBoundingClientRect().bottom
                - article.getBoundingClientRect().top          // from border-top edge
                + px(getComputedStyle(lastVisible).marginBottom)
                + oneEm();                                      // artificial final margin
            return b.borderBox ? span + b.padB + b.borB : span - b.borT - b.padT;
        };

        // Natural (unclipped) height. scrollHeight = content + padding, and it
        // reports full content even while the box is clipped. Used only as the
        // animation end-point; afterwards the inline height is removed.
        const fullHeight = () => {
            const b = boxInfo();
            const sh = article.scrollHeight;
            return b.borderBox ? sh + b.borT + b.borB : sh - b.padT - b.padB;
        };

        // ---- transition plumbing -------------------------------------------

        const transitionMs = () => {
            const cs = getComputedStyle(article);
            const ms = (v) => (v.trim().endsWith("ms") ? px(v) : px(v) * 1000);
            const max = (list) => Math.max(0, ...list.split(",").map(ms));
            return max(cs.transitionDuration) + max(cs.transitionDelay);
        };

        // Run fn once the article's own height transition ends or is cancelled,
        // with a timeout fallback (transitionend does not fire if no transition
        // ran). Returns a canceller.
        const afterHeightTransition = (fn) => {
            let done = false;
            const onEnd = (e) => {
                // transitionend bubbles: ignore descendants and other properties
                if (e.target === article && e.propertyName === "height") finish();
            };
            const cleanup = () => {
                done = true;
                clearTimeout(timer);
                article.removeEventListener("transitionend", onEnd);
                article.removeEventListener("transitioncancel", onEnd);
            };
            const finish = () => { if (!done) { cleanup(); fn(); } };
            article.addEventListener("transitionend", onEnd);
            article.addEventListener("transitioncancel", onEnd);
            const timer = setTimeout(finish, transitionMs() + 50);
            return cleanup;
        };

        let cancelPending = () => {};

        const withoutTransition = (fn) => {
            const saved = article.style.transition;
            article.style.transition = "none";
            fn();
            void article.offsetHeight;      // flush style so "none" applies
            article.style.transition = saved;
        };

        // ---- state changes -------------------------------------------------

        const collapse = (animate) => {
            const target = collapsedHeight();
            if (!animate) {
                withoutTransition(() => { article.style.height = target + "px"; });
                return;
            }
            article.style.height = currentStyleHeight() + "px";   // freeze from auto
            void article.offsetHeight;                            // start point
            article.style.height = target + "px";
        };

        const expand = (animate) => {
            if (!animate) {
                withoutTransition(() => { article.style.height = ""; });
                return;
            }
            const from = currentStyleHeight();
            const to = fullHeight();
            article.style.height = from + "px";
            void article.offsetHeight;
            article.style.height = to + "px";
            if (Math.abs(to - from) < 1) {        // nothing to animate
                article.style.height = "";
                return;
            }
            cancelPending = afterHeightTransition(() => { article.style.height = ""; });
        };

        // ---- persisted state -----------------------------------------------

        const storedState = localStorage.getItem(articleId);
        let isCollapsed = (storedState === null)
            ? index !== 0                       // first visit: collapse all but first
            : storedState === "collapsed";

        const render = (animate) => {
            toggleSpan.textContent = isCollapsed ? "Expand ▼" : "Collapse ▲";
            localStorage.setItem(articleId, isCollapsed ? "collapsed" : "expanded");
            article.classList.toggle("collapsed", isCollapsed);
            if (isCollapsed) collapse(animate); else expand(animate);
        };

        render(false);

        // Keep the collapsed height right as images/fonts load above the cut,
        // or as the window width changes text wrapping.
        const ro = new ResizeObserver(() => {
            if (isCollapsed) article.style.height = collapsedHeight() + "px";
        });
        children.slice(0, children.indexOf(lastVisible) + 1).forEach((el) => ro.observe(el));

        toggleSpan.addEventListener("click", () => {
            cancelPending();                    // abandon a half-finished expand
            cancelPending = () => {};
            isCollapsed = !isCollapsed;
            render(true);
        });
    });
});