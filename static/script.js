document.addEventListener("DOMContentLoaded", () => {
    // ---------------------------------------------
    // Autocomplete Search Suggestions
    // ---------------------------------------------
    const searchInput = document.getElementById("song-search");
    const suggestionsBox = document.getElementById("search-suggestions");
    const searchForm = document.getElementById("search-form");

    if (searchInput && suggestionsBox) {
        let debounceTimer;

        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            const query = searchInput.value.trim();

            if (query.length < 2) {
                suggestionsBox.style.display = "none";
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/search_suggestions?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        suggestionsBox.innerHTML = "";
                        if (data.length === 0) {
                            suggestionsBox.style.display = "none";
                            return;
                        }

                        data.forEach(item => {
                            const div = document.createElement("div");
                            div.className = "suggestion-item";
                            
                            // Create HTML content for recommendation suggestion
                            div.innerHTML = `
                                <div class="suggestion-info">
                                    <div class="suggestion-title">${item.song}</div>
                                    <div class="suggestion-artist">${item.artist}</div>
                                </div>
                                <span class="suggestion-badge">${item.genre}</span>
                            `;

                            div.addEventListener("click", () => {
                                searchInput.value = item.song;
                                suggestionsBox.style.display = "none";
                                // Submit the form automatically
                                if (searchForm) {
                                    searchForm.submit();
                                }
                            });

                            suggestionsBox.appendChild(div);
                        });
                        suggestionsBox.style.display = "block";
                    })
                    .catch(err => console.error("Autocomplete error:", err));
            }, 250);
        });

        // Hide suggestions when clicking outside
        document.addEventListener("click", (e) => {
            if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.style.display = "none";
            }
        });
    }

    // ---------------------------------------------
    // Add to Playlist Dropdowns
    // ---------------------------------------------
    const playlistToggleBtns = document.querySelectorAll(".action-dropdown-btn");
    
    playlistToggleBtns.forEach(btn => {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const parent = btn.parentElement;
            const menu = parent.querySelector(".dropdown-menu");
            
            // Close other open menus
            document.querySelectorAll(".dropdown-menu").forEach(m => {
                if (m !== menu) m.classList.remove("show-dropdown");
            });
            
            if (menu) menu.classList.toggle("show-dropdown");
        });
    });

    // Close dropdowns on outside click
    document.addEventListener("click", () => {
        document.querySelectorAll(".dropdown-menu").forEach(m => {
            m.classList.remove("show-dropdown");
        });
    });
});
