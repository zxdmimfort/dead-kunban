class DraggableBoard {
  constructor(containerSelector, boardSelector) {
    this.container = document.querySelector(containerSelector);
    this.board = document.querySelector(boardSelector);
    this.scale = 1;
    this.isDraggingBoard = false;
    this.lastX = 0;
    this.lastY = 0;

    this.selectedCard = null;
    this.selectedID = null;
    this.selectedCardModel = null;
    this.isDraggingCard = false

    if (!this.isMobileDevice()) {
      this.initDesktopEvents();
    } else {
      this.disableDesktopEvents();
    }


    this.updateSelectionAndDragEventListeners();
    const statuses = ["todo", "inprogress", "done", "rest", "archived"];
    document.querySelectorAll("div.column").forEach((column, index) => {
      column.addEventListener("mouseenter", () => {
        if (this.isDraggingCard)
                if ( this.selectedCardModel!==null && this.selectedCardModel.status!=statuses[index] ) {
                    this.selectedCardModel.setStatus(statuses[index]);
                    kanban.model.cards[this.selectedID] = this.selectedCardModel;
                    kanban.push()
                    kanban.sync()
                    this.selectedCard = null;
                    this.selectedID = null;
                    this.selectedCardModel = null;
                    this.isDraggingCard=false
                }
      });
    })
  }

  // Check if the device is mobile
  isMobileDevice() {
    return /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  }

  // Apply transform to the board
  applyTransform(translateX = 0, translateY = 0) {
    this.board.style.transform = `translate(${translateX}px, ${translateY}px) scale(${this.scale})`;
  }

  // Zoom in functionality
  zoomIn() {
    this.scale += 0.1;
    this.applyTransform();
  }

  // Zoom out functionality
  zoomOut() {
    if (this.scale > 0.1) {
      this.scale -= 0.1;
      this.applyTransform();
    }
  }

  // Initialize desktop-specific events for the board
  initDesktopEvents() {
    const handleMouseDown = (e) => {
      if (e.button === 1) { // Middle mouse button
        this.isDraggingBoard = true;
        this.lastX = e.clientX;
        this.lastY = e.clientY;
      }
    };

    const handleMouseMove = (e) => {
      if (this.isDraggingBoard) {
        const dx = e.clientX - this.lastX;
        const dy = e.clientY - this.lastY;
        const currentTransform = window.getComputedStyle(this.board).transform;
        const matrix = new DOMMatrix(currentTransform);
        const translateX = (matrix.e || 0) + 2 * dx;
        const translateY = (matrix.f || 0) + 5 * dy;

        this.applyTransform(translateX, translateY);
        this.lastX = e.clientX;
        this.lastY = e.clientY;
      }
    };

    const handleMouseUp = () => {
      this.isDraggingBoard = false;
    };

    const handleMouseLeave = () => {
      this.isDraggingBoard = false;
    };

    const handleWheel = (e) => {
      e.preventDefault();
      if (e.deltaY < 0) {
        this.zoomIn();
      } else {
        this.zoomOut();
      }
    };

    this.container.addEventListener('mousedown', handleMouseDown);
    this.container.addEventListener('mousemove', handleMouseMove);
    this.container.addEventListener('mouseup', handleMouseUp);
    this.container.addEventListener('mouseleave', handleMouseLeave);
    this.container.addEventListener('wheel', handleWheel);

  }

  // Disable desktop-specific events for the board
  disableDesktopEvents() {
    this.container.removeEventListener('mousedown', null);
    this.container.removeEventListener('mousemove', null);
    this.container.removeEventListener('mouseup', null);
    this.container.removeEventListener('mouseleave', null);
    this.container.removeEventListener('wheel', null);
  }

  // Update card selection and drag event listeners
  updateSelectionAndDragEventListeners() {
    document.querySelectorAll('.card').forEach((card) => {
      let isDraggingCard = false;
      let cardStartX = 0;
      let cardStartY = 0;
      let initialCardTranslateX = 0;
      let initialCardTranslateY = 0;

      // Store the original position of the card
      const startCardDrag = (e) => {
//        e.stopPropagation(); // Prevent event bubbling to the board
        isDraggingCard = true;
        cardStartX = e.clientX;
        cardStartY = e.clientY;

        const cardStyle = window.getComputedStyle(card);
        const matrix = new DOMMatrix(cardStyle.transform);
        initialCardTranslateX = matrix.e || 0;
        initialCardTranslateY = matrix.f || 0;

        card.classList.add('dragging');
      };

      const dragCard = (e) => {
        if (isDraggingCard) {
          const dx = e.clientX - cardStartX;
          const dy = e.clientY - cardStartY;
          this.translateX = initialCardTranslateX + dx;
          this.translateY = initialCardTranslateY + dy;

          card.style.transform = `translate(${this.translateX}px, ${this.translateY}px)`;
        }
      };

      const endCardDrag = () => {
        isDraggingCard = false;
        card.classList.remove('dragging');
        // Reset the card to its original position
        card.style.transform = `translate(${0}px, ${0}px)`;

      };

      card.addEventListener('mousedown', (e) => {
            if (e.button === 0) { // Left mouse button
              startCardDrag(e);
            }
      });

      document.addEventListener('mousemove', dragCard);
      document.addEventListener('mouseup', endCardDrag);
      card.addEventListener('mousedown', (e) => {
            e.preventDefault();
            if (this.selectedCard!== null) {
                //remove previously selected card if it is stored
                if (this.selectedCard !== card) {
                    this.selectedCard.classList.remove('selected');
                        card.classList.add('selected');
                        this.selectedCard = card;
                        this.selectedID = parseInt(card.id.replace('card_', ''));
                        this.selectedCardModel = kanban.model.cards[this.selectedID];
                } else {
                    card.classList.remove('selected');
                    this.selectedCard = null;
                    this.selectedID = null;
                    this.selectedCardModel = null;
                }
            } else if (this.selectedCard=== null) {
                card.classList.add('selected');
                this.selectedCard = card;
                this.selectedID = parseInt(card.id.replace('card_', ''));
                this.selectedCardModel = kanban.model.cards[this.selectedID];
            }
            this.isDraggingCard = true;
      });



      card.addEventListener('mouseup', (e) => {
        if ( (Math.abs(this.translateX) > 50 || Math.abs(this.translateY) > 50) ){
                card.classList.remove('selected');
                this.translateX=0;
                this.translateY=0;
          } else {
              this.isDraggingCard = false;
          }
      });



      // Add touch event listeners for mobile compatibility
      card.addEventListener('touchstart', (e) => {
        e.preventDefault(); // Prevent default touch behavior
        startCardDrag(e.touches[0]);
      });
      card.addEventListener('touchmove', (e) => {
        e.preventDefault(); // Prevent scrolling while dragging
        dragCard(e.touches[0]);
      });
      card.addEventListener('touchend', () => {
        endCardDrag();
      });

      card.addEventListener('touchend', () => {
        endCardDrag();
      });
      // Reset card position on mouse leave
      card.addEventListener('mouseleave', () => {
        if (!isDraggingCard) {
          card.style.transform = `translate(${0}px, ${0}px)`;
        }
      });
    });
  }

}

// Initialize the KanbanBoard instance
const draggableBoard = new DraggableBoard('#kanbanContainer', '#kanbanBoard');

