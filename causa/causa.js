(() => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce) document.documentElement.classList.add("motion");

  const progress = document.querySelector(".progress");
  const chapters = [...document.querySelectorAll(".chapter")];
  const screens = [...document.querySelectorAll(".screen")];
  const ground = document.querySelector(".ground");
  const chapterRoot = document.querySelector(".chapters");

  const setTheme = (theme) => {
    document.body.dataset.theme = theme;
    chapterRoot.style.setProperty(
      "--chapter-ink",
      theme === "dark" ? "#f2f0f0" : "#182124",
    );
  };

  const activate = (chapter) => {
    const theme = chapter.dataset.theme || "light";
    setTheme(theme);
    ground.style.setProperty("--ground", chapter.dataset.bg || "#f2f0f0");
    const wanted = chapter.dataset.screen;
    screens.forEach((img) => img.classList.toggle("active", img.dataset.screen === wanted));
    const ghost = document.getElementById("stage-ghost");
    if (ghost && chapter.dataset.ghost) ghost.textContent = chapter.dataset.ghost;
  };

  const chapterObserver = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
      if (visible) activate(visible.target);
    },
    { rootMargin: "-38% 0px -38% 0px", threshold: [0, 0.2, 0.5, 0.8] },
  );
  chapters.forEach((c) => chapterObserver.observe(c));

  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          revealObserver.unobserve(e.target);
        }
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 },
  );
  document.querySelectorAll(".reveal").forEach((el) => revealObserver.observe(el));

  const navSections = [...document.querySelectorAll("[data-nav]")];
  const updateNav = () => {
    const y = 92;
    let current = navSections[0];
    for (const section of navSections) {
      const rect = section.getBoundingClientRect();
      if (rect.top <= y && rect.bottom > y) current = section;
    }
    if (current) document.body.dataset.nav = current.dataset.nav || "dark";
  };

  let raf = 0;
  const onScroll = () => {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      raf = 0;
      const max = document.documentElement.scrollHeight - innerHeight;
      progress.style.width = max > 0 ? `${(scrollY / max) * 100}%` : "0%";
      updateNav();
      if (scrollY < chapterRoot.offsetTop - innerHeight * 0.5) {
        setTheme("dark");
        ground.style.setProperty("--ground", "#182124");
        screens.forEach((img, i) => img.classList.toggle("active", i === 0));
      } else {
        const mid = innerHeight * 0.62;
        const current =
          chapters.find((c) => {
            const r = c.getBoundingClientRect();
            return r.top <= mid && r.bottom > mid;
          }) ||
          chapters.find((c) => c.getBoundingClientRect().top >= 0) ||
          chapters[0];
        if (current) activate(current);
      }
    });
  };
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  updateNav();

  const video = document.getElementById("demo-video");
  const chapterButtons = [...document.querySelectorAll(".video-chapters button")];
  if (video && chapterButtons.length) {
    chapterButtons.forEach((button) => {
      button.addEventListener("click", () => {
        video.currentTime = Number(button.dataset.time || 0);
        video.play().catch(() => {});
      });
    });
    video.addEventListener("timeupdate", () => {
      const t = video.currentTime;
      let active = 0;
      chapterButtons.forEach((button, i) => {
        if (t >= Number(button.dataset.time || 0)) active = i;
      });
      chapterButtons.forEach((button, i) => button.classList.toggle("active", i === active));
    });
  }

  document.querySelector("[data-copy-sha]")?.addEventListener("click", async (event) => {
    const sha = "633d8ab13d554b4a8b4f61cc6823df3908b4ba664e9194fd7d4b0b7747ef6624";
    const button = event.currentTarget;
    try {
      await navigator.clipboard.writeText(sha);
      button.textContent = "已复制";
    } catch {
      button.textContent = "复制失败，请手动选择";
    }
    setTimeout(() => (button.textContent = "复制校验和"), 1800);
  });
})();
