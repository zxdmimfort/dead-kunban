function newCard(id, el) {
//    return `
//        <div class="column" id=kanban_${id}>
//            <h2>${name}</h2>
//            <div class="card">${details}</div>
//        </div>
//    `;
    function next_job(){
        if (el.days_till_todo > 0 ) {
            return  `<br>Следующее задание: ${el.cooldown} (через ${el.days_till_todo} дней )` ;
        } else if (el.hours_till_todo !=-1) {
            return  `<br>Следующее задание: ${el.cooldown} (через ${el.hours_till_todo} часа)` ;
        } else return ""
    }
    return `<div class="card" id="card_${id}"> <h5>${el.title}</h5>
     ${el.description}
    <span style="font-size: 10px;">
        <br>Период оборота: <span style="font-size: 12px; font-weight: 700;">${el.period}</span> дней
        ${next_job()}
        <br>Последний статус: ${el.history_as_string} <br></div>
    </span>
    `;

}
async function post(yourUrl, data) {
    try {
        let request =  {
            method: "POST",
            headers: {
               'Content-Type': 'application/json'
            },
            body: JSON.stringify(  data )
        }
        const response = await fetch(yourUrl, request);

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return await response.json(); // Optionally return the response data as JSON
    } catch (error) {
        console.error("Error during POST request:", error);
        throw error; // Re-throw the error for further handling if needed
    }
}

async function get(yourUrl) {
    try {
        const response = await fetch(yourUrl);
        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }
        const data = await response.json(); // Automatically parses JSON
        return data;
    } catch (error) {
        console.error('Error fetching data:', error.message);
        throw error; // Re-throw the error for further handling
    }
}

class Card {
    // Constructor to initialize card properties
    constructor(id=0, title="", description="", assignee="", status="", dueDate="", priority = "normal", period="-1", createdAt = new Date()) {
        this.id = id; // Unique identifier for the card
        this.title = title; // Title of the card
        this.description = description || ''; // Optional description
        this.assignee = assignee; // Person responsible for the task
        this.status = status; // Current status (e.g., 'To Do', 'In Progress', 'Done')
        this.dueDate = dueDate; // Due date for the task
        this.priority = priority; // Priority level (e.g., 'low', 'normal', 'high')
        this.createdAt = createdAt; // Timestamp when the card was created
        this.period = period; // regularity
//        this.regular = ;
//        this.comments = []; // Array to store comments
//        this.attachments = []; // Array to store attachments
        this.history = [{ status: this.status, timestamp: this.createdAt }]; // Track status changes
    }

    // Method to update card details
    update({ title, description, assignee, status, dueDate, priority, period }) {
        if (title !== undefined) this.title = title;
        if (description !== undefined) this.description = description;
        if (assignee !== undefined) this.assignee = assignee;
        if (status !== undefined) {
            this.setStatus(status);
        }
        if (dueDate !== undefined) this.dueDate = dueDate;
        if (priority !== undefined) this.priority = priority;
        if (period !== undefined) this.period= period;
    }

    // Method to set or change the status and log history
    setStatus(newStatus) {
        if (newStatus !== this.status) {
            this.history.push({ status: newStatus, timestamp: new Date() });
            this.status = newStatus;
        }
    }

    // Method to add a comment
    addComment(comment) {
        this.comments.push({ text: comment, timestamp: new Date() });
    }

    // Method to add an attachment
    addAttachment(file) {
        this.attachments.push(file);
    }

    // Method to check if the card is overdue
    isOverdue() {
        return new Date() > this.dueDate && this.status !== 'Done';
    }
};
class Kanban {

    constructor() {
        this.columns = []
        this.cards = []
    }
};

class KanbanController {
    constructor() {
        this.create_card = document.querySelector('#kanban_create_card');
        this.edit_card = document.querySelector('#kanban_edit_card');
        this.create_col = document.querySelector('#kanban_create_column');
//        this.kanban_push = document.querySelector('#kanban_push');
//        this.kanban_sync = document.querySelector('#kanban_sync');
        this.kanban_delete = document.querySelector('#kanban_delete');
        this.kanban_duplicate = document.querySelector('#kanban_duplicate');
        this.kanban_invisible = document.querySelector('#kanban_invisible');

        this.container = document.querySelector('div.kanban-container');
        this.model = new Kanban();

        this.create_card.addEventListener('click', e => {
            showGently(draggableDialog.dialog.style);
            // Append data to the FormData object
            document.querySelector('#cardForm #title').value ='';
            document.querySelector('#cardForm #status').value ='';
            document.querySelector('#cardForm #description').value = '';
            document.querySelector('#cardForm #assignee').value = '';
            document.querySelector('#cardForm #status').value='';
            document.querySelector('#cardForm #dueDate').value='';
            document.querySelector('#cardForm #priority').value='';

            document.querySelector('.dialog-footer button.update').style.display='none';
            document.querySelector('.dialog-footer button.create').style.display='';
          });

        this.edit_card.addEventListener('click', e => {
            if (draggableBoard.selectedCard!==null) {
                showGently(draggableDialog.dialog.style);
                document.querySelector('#cardForm #title').value =draggableBoard.selectedCardModel.title;
                document.querySelector('#cardForm #status').value = draggableBoard.selectedCardModel.status;
                document.querySelector('#cardForm #description').value = draggableBoard.selectedCardModel.description;
                document.querySelector('#cardForm #assignee').value = draggableBoard.selectedCardModel.assignee;
                document.querySelector('#cardForm #status').value=draggableBoard.selectedCardModel.status;
                document.querySelector('#cardForm #dueDate').value=draggableBoard.selectedCardModel.dueDate;
                document.querySelector('#cardForm #priority').value=draggableBoard.selectedCardModel.priority;

                document.querySelector('.dialog-footer button.update').style.display='';
                document.querySelector('.dialog-footer button.create').style.display='none';

            };
        });
//        this.kanban_push.addEventListener('click', e => {
//            this.push();
//        });
//
        this.kanban_delete.addEventListener('click', e => {
            if (draggableBoard.selectedCard!== null){
                this.model.cards.splice( draggableBoard.selectedID, 1 );
                this.push();
                this.sync();
            }
        });
        this.kanban_duplicate.addEventListener('click', e => {
            if (draggableBoard.selectedCard !== null){
                this.model.cards.splice(draggableBoard.selectedID, 0, draggableBoard.selectedCardModel);
                this.push();
                this.sync();
            }
        });

        this.kanban_invisible.addEventListener('change', e => {
            console.log(this.kanban_invisible.checked)
            if (this.kanban_invisible.checked) {
                let columns = document.querySelectorAll(".kanban-board > .column[hidden]")
                columns.forEach((el)=> showGently(el.style))
            } else {
                let columns = document.querySelectorAll(".kanban-board > .column[hidden]")
                columns.forEach((el)=> hideGently(el.style))
            }
        });
    }

    push() {
        post('/kanban_push', this.model);
        this.sync();
    }
//    export(){
//        get('/kanban_pull')
//        .then(data => {
//            console.log('Data received:', data);
//            return data;
//        })
//        .catch(error => {
//            console.error('Error fetching data:', error.message);
//        });
//    }

    sync(){
        get('/kanban_pull')
        .then(data => {
            console.log('Data received:', data);
            this.model = new Kanban();
            if (data.cards && Array.isArray(data.cards)) {
                this.model.cards = data.cards.map(cardData => {
                    const card = new Card();
                    Object.assign(card, cardData);
                    return card;
                });
//                kanban.model.columns = data.columns.map(colData => {
//                    let status = document.querySelector('select#status');
//                    status.innerHTML += `<option value="${colData}">${colData}</option>`
//                    return colData;
//                });

                let kanbancontainer = document.querySelectorAll('div#kanbanBoard > .column');
                kanbancontainer.forEach( (el) => {el.innerHTML = ''})

                let i=0;
                this.cardToHtmlMap = [];
                const statuses = ["todo", "inprogress", "done", "rest", "archived"]
                kanbancontainer[0].innerHTML +='<h3>To Do</h3>';
                kanbancontainer[1].innerHTML +='<h3>In Progress</h3>';
                kanbancontainer[2].innerHTML +='<h3>Done</h3>';
                kanbancontainer[3] .innerHTML +='<h3>Rest</h3>';
                kanbancontainer[4] .innerHTML +='<h3>Archived</h3>';

                if (this.kanban_invisible.checked) {
                    let columns = document.querySelectorAll(".kanban-board > .column[hidden]")
                    columns.forEach((el)=> showGently(el.style))
                } else {
                    let columns = document.querySelectorAll(".kanban-board > .column[hidden]")
                    columns.forEach((el)=> hideGently(el.style))
                }

                [0,1,2,3,4].forEach((index)=> {
                    this.model.cards.forEach( (el, i) => {
                        if (el.status== statuses[index]){
                            kanbancontainer[index].innerHTML += newCard(i, el);
    //                    this.cardToHtmlMap[i++] = el;
                        }
                    } );
                })
            } else {
                this.model.cards = [];
            }
            draggableBoard.updateSelectionAndDragEventListeners();
            console.log('Kanban model populated:', kanban.model);
        })
        .catch(error => {
            console.error('Error fetching data:', error.message);
        });

    }
};

const kanban = new KanbanController();
kanban.sync();