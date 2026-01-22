/**
 * Phase 2 UI Skeleton — app.js
 * 
 * Governance: No data, no computation, no persistence.
 * Toggles affect visibility of placeholders only.
 * Frame switching carries no implicit meaning.
 */

(function () {
    'use strict';

    // DOM References
    const frameButtons = document.querySelectorAll('.frame-button');
    const frameViews = document.querySelectorAll('.frame-view');
    const noFrameSelected = document.getElementById('no-frame-selected');
    const indicatorToggles = document.querySelectorAll('.indicator-toggle');

    // State (UI-only, not persisted)
    let activeFrame = null;

    /**
     * Initialize UI skeleton
     * No frame is selected by default (governance compliance)
     */
    function init() {
        // Bind frame selector buttons
        frameButtons.forEach(button => {
            button.addEventListener('click', handleFrameSelect);
        });

        // Bind indicator toggles
        indicatorToggles.forEach(toggle => {
            toggle.addEventListener('change', handleToggleChange);
        });

        // Ensure neutral starting state
        showNoFrameSelected();
    }

    /**
     * Handle frame selection
     * Does not imply priority or meaning
     */
    function handleFrameSelect(event) {
        const button = event.currentTarget;
        const frameId = button.dataset.frame;

        // Update button states
        frameButtons.forEach(btn => {
            btn.setAttribute('aria-selected', btn === button ? 'true' : 'false');
        });

        // Show selected frame view
        activeFrame = frameId;
        showFrameView(frameId);
    }

    /**
     * Show the selected frame view
     */
    function showFrameView(frameId) {
        // Hide all frames
        frameViews.forEach(view => {
            view.hidden = true;
        });

        // Hide no-selection state
        noFrameSelected.style.display = 'none';

        // Show target frame
        const targetView = document.querySelector(`.frame-view[data-frame="${frameId}"]`);
        if (targetView) {
            targetView.hidden = false;
        }
    }

    /**
     * Show the no-frame-selected state
     */
    function showNoFrameSelected() {
        frameViews.forEach(view => {
            view.hidden = true;
        });
        noFrameSelected.style.display = 'flex';
    }

    /**
     * Handle indicator toggle change
     * Affects placeholder visibility only — no computation
     */
    function handleToggleChange(event) {
        const toggle = event.currentTarget;
        const indicator = toggle.dataset.indicator;
        const isChecked = toggle.checked;

        // Find associated empty state in the same frame view
        const frameView = toggle.closest('.frame-view');
        if (frameView) {
            const emptyState = frameView.querySelector('.empty-state');
            if (emptyState) {
                // Toggle visibility of empty state placeholder
                // When indicator is "on", placeholder is visible
                // When indicator is "off", placeholder is hidden
                emptyState.style.opacity = isChecked ? '1' : '0.3';
            }
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
