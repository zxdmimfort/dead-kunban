export default class Card {
    constructor(
      id=0, 
      title="", 
      description="", 
      assignee="", 
      status="", 
      dueDate="", 
      priority = "normal", 
      period="-1", 
      createdAt = new Date()) {
        
        this.id = id;
        this.title = title;
        this.description = description || '';
        this.assignee = assignee;
        this.status = status;
        this.dueDate = dueDate;
        this.priority = priority;
        this.createdAt = createdAt; 
        this.period = period; // regularity
  //        this.regular = ;
  //        this.comments = [];
  //        this.attachments = [];
        this.history = [{ status: this.status, timestamp: this.createdAt }];
    }
  
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
    setStatus(newStatus) {
        if (newStatus !== this.status) {
            this.history.push({ status: newStatus, timestamp: new Date() });
            this.status = newStatus;
        }
    }
    addComment(comment) {
        this.comments.push({ text: comment, timestamp: new Date() });
    }
    addAttachment(file) {
        this.attachments.push(file);
    }
    isOverdue() {
        return new Date() > this.dueDate && this.status !== 'Done';
    }
  };