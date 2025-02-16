class DraggableDialog {
  constructor(dialogSelector, headerSelector) {
    this.dialog = document.querySelector(dialogSelector);
    this.header = document.querySelector(headerSelector);
    this.isDragging = false;
    this.startX = 0;
    this.startY = 0;
    this.deltaX = 0;
    this.deltaY = 0;

    // Add event listeners for both mouse and touch events
    if (this.header) {
      this.header.addEventListener('mousedown', this.onMouseDown.bind(this));
      this.header.addEventListener('touchstart', this.onTouchStart.bind(this));
    }

    this.cancel = document.querySelector('.dialog-footer button.cancel');
    this.create = document.querySelector('.dialog-footer button.create');
    this.update = document.querySelector('.dialog-footer button.update');

    this.cancel.addEventListener('click', () => { hideGently(this.dialog.style); });
  }

  // Mouse event handlers
  onMouseDown(e) {
    e.preventDefault();
    this.isDragging = true;
    const rect = this.dialog.getBoundingClientRect();
    this.startX = e.clientX;
    this.startY = e.clientY;
    this.deltaX = this.startX - rect.left;
    this.deltaY = this.startY - rect.top;

    document.addEventListener('mousemove', this.onMouseMove.bind(this));
    document.addEventListener('mouseup', this.onMouseUp.bind(this));
  }

  onMouseMove(e) {
    if (!this.isDragging) return;
    const newX = coerceIn(e.clientX - this.deltaX, 0, document.documentElement.clientWidth);
    const newY = coerceIn(e.clientY - this.deltaY, 0, document.documentElement.clientHeight);

    this.dialog.style.left = `${newX}px`;
    this.dialog.style.top = `${newY}px`;
  }

  onMouseUp() {
    this.isDragging = false;
    document.removeEventListener('mousemove', this.onMouseMove.bind(this));
    document.removeEventListener('mouseup', this.onMouseUp.bind(this));
  }

  // Touch event handlers
  onTouchStart(e) {
    e.preventDefault();
    this.isDragging = true;
    const touch = e.touches[0];
    const rect = this.dialog.getBoundingClientRect();
    this.startX = touch.clientX;
    this.startY = touch.clientY;
    this.deltaX = this.startX - rect.left;
    this.deltaY = this.startY - rect.top;

    document.addEventListener('touchmove', this.onTouchMove.bind(this));
    document.addEventListener('touchend', this.onTouchEnd.bind(this));
  }

  onTouchMove(e) {
    if (!this.isDragging) return;
    const touch = e.touches[0];
    const newX = coerceIn(touch.clientX - this.deltaX, 0, document.documentElement.clientWidth);
    const newY = coerceIn(touch.clientY - this.deltaY, 0, document.documentElement.clientHeight);

    this.dialog.style.left = `${newX}px`;
    this.dialog.style.top = `${newY}px`;
  }

  onTouchEnd() {
    this.isDragging = false;
    document.removeEventListener('touchmove', this.onTouchMove.bind(this));
    document.removeEventListener('touchend', this.onTouchEnd.bind(this));
  }
}

// Helper function to constrain values within a range
function coerceIn(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

// Initialize the draggable dialog
const draggableDialog = new DraggableDialog('.dialog-container', '.dialog-header');

draggableDialog.create.addEventListener('click', () => {
    //create
    fd = new FormData(document.querySelector('#cardForm'));
    let card1 = new Card(
        1,
        fd.get("title"), // Use key directly, not an array
        fd.get("description"),
        fd.get("assignee"),
        fd.get("status"),
        fd.get("dueDate"),
        fd.get("priority"),
        fd.get("period"),
    );
    kanban.model.cards.push(card1);
    kanban.push();
    kanban.sync();
});

draggableDialog.update.addEventListener('click', () => {
    // edit
    fd = new FormData(document.querySelector('#cardForm'));
    draggableBoard.selectedCardModel.update({
        "title":fd.get("title"),
        "description":fd.get("description"),
        "assignee":fd.get("assignee"),
        "status":fd.get("status"),
        "dueDate":fd.get("dueDate"),
        "priority":fd.get("priority"),
        "period":fd.get("period"),
    });
    kanban.model.cards[draggableBoard.selectedID] = draggableBoard.selectedCardModel;
    kanban.push();
    kanban.sync();
});


document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
      if (draggableDialog.dialog.style.display != 'none') {
            hideGently(draggableDialog.dialog.style);
      }
    }
  })
