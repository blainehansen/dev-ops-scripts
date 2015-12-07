db = new Mongo().getDB("meteor");

// Dates
var payment, lesson, expense, date;

var payments = db.payments.find({});
while (payments.hasNext()) {
	payment = payments.next();
	printjson(payment);

	date = payment.date
	printjson(date);

	date = date.split('/');
	printjson(date);

	date = new Date(date[2], date[0] - 1, date[1]);
	printjson(date);

	// db.payments.update(id, {$set: {date: date}});
}

var lessons = db.lessons.find({});
while (lessons.hasNext()) {
	lesson = lessons.next();
	printjson(lesson);

	date = lesson.date
	printjson(date);

	date = date.split('/');
	printjson(date);

	date = new Date(date[2], date[0] - 1, date[1]);
	printjson(date);

	// db.lessons.update(id, {$set: {date: date}});
}

var expenses = db.expenses.find({});
while (expenses.hasNext()) {
	expense = expenses.next();
	printjson(expense);

	date = expense.date
	printjson(date);

	date = date.split('/');
	printjson(date);

	date = new Date(date[2], date[0] - 1, date[1]);
	printjson(date);

	// db.expenses.update(id, {$set: {date: date}});
}




// Object relations
// users: payments, students
var users = db.users.find({});
var user, payment_ids, student_ids, index, id;
while (users.hasNext()) {
	user = users.next();
	printjson(user);

	payment_ids = user.payment_ids;
	for (index in payment_ids) {
		id = payment_ids[index];
		// update that payment with the user_id
		// db.payments.update(id, {$set: {user_id: user._id}});
	}

	student_ids = user.student_ids;
	for (index in student_ids) {
		id = student_ids[index];
		// update that student with the user_id
		// db.students.update(id, {$set: {user_id: user._id}});
	}

	// update the user to delete the arrays on the user.
	// db.users.update(user, {$unset: {payment_ids: "", student_ids: ""}});
}

// students: lessons, studentexpenses
var students = db.students.find({});
var student, lesson_ids, expense_ids;
while (students.hasNext()) {
	student = students.next();
	printjson(student);

	lesson_ids = student.lesson_ids;
	for (index in lesson_ids) {
		id = lesson_ids[index];
		// update that lesson with the student_id
		// db.lessons.update(id, {$set: {student_id: student._id}});
	}

	expense_ids = student.expense_ids;
	for (index in expense_ids) {
		id = expense_ids[index];
		// update that expense with the student_id
		// db.studentexpenses.update(id, {$set: {student_id: student._id}});
	}
	
	// update the student to delete the arrays on the student.
	// db.students.update(user, {$unset: {lesson_ids: "", expense_ids: ""}});
}