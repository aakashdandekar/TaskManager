let tasks = [];

function loadTasks() {
  const username = sessionStorage.getItem('username');
  const password = sessionStorage.getItem('password');
  
  if (!username || !password) {
    window.location.href = '/login';
    return;
  }

  fetch('/view_data', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username, password})
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      window.location.href = '/login';
    } else if (data.data) {
      tasks = data.data;
      displayTasks();
    }
  })
  .catch(() => {
    window.location.href = '/login';
  });
}

function addTask() {
  const taskInput = document.getElementById('taskInput');
  const taskText = taskInput.value.trim();
  
  if (taskText === '') return;

  const username = sessionStorage.getItem('username');
  const password = sessionStorage.getItem('password');

  const newTask = {text: taskText};
  tasks.push(newTask);

  fetch('/add_data', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username,
      password,
      item: tasks
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.data) {
      tasks = data.data;
      displayTasks();
      taskInput.value = '';
    }
  });
}

function displayTasks() {
  const taskList = document.getElementById('taskList');
  taskList.innerHTML = '';

  tasks.forEach((task, index) => {
    const li = document.createElement('li');
    li.innerHTML = `
      <input type="checkbox" onchange="toggleTask(${index})">
      <span>${task.text}</span>
    `;
    taskList.appendChild(li);
  });
}

function toggleTask(index) {
  tasks.splice(index, 1);
  
  const username = sessionStorage.getItem('username');
  const password = sessionStorage.getItem('password');

  fetch('/add_data', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username,
      password,
      item: tasks
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.data) {
      tasks = data.data;
      displayTasks();
    }
  });
}

function logout() {
  sessionStorage.removeItem('username');
  sessionStorage.removeItem('password');
  window.location.href = '/login';
}

function checkAdmin() {
  const username = sessionStorage.getItem('username');
  if (username === 'admin') {
    window.location.href = '/admin';
  }
}

function showProfileOverlay() {
  document.getElementById('profileOverlay').style.display = 'block';
}

function closeProfileOverlay() {
  document.getElementById('profileOverlay').style.display = 'none';
  document.getElementById('profileForm').reset();
  document.getElementById('profileMessage').innerHTML = '';
}

document.addEventListener('DOMContentLoaded', function() {
  loadTasks();
  
  const username = sessionStorage.getItem('username');
  
  // Show admin button if user is admin
  if (username === 'admin') {
    document.getElementById('adminBtn').style.display = 'block';
  } else {
    // Show profile button for regular users
    document.getElementById('profileBtn').style.display = 'block';
  }
  
  // Add Enter key support for task input
  document.getElementById('taskInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      addTask();
    }
  });
  
  // Profile form submission
  document.getElementById('profileForm').onsubmit = function(e) {
    e.preventDefault();
    
    const newPassword = document.getElementById('newPassword').value;
    console.log('Updating password for user:', username);
    
    fetch('/update_password', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        username: username,
        new_password: newPassword
      })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Password update response:', data);
      document.getElementById('profileMessage').innerHTML = data.message || data.error;
      if (data.message) {
        // Update stored password
        sessionStorage.setItem('password', newPassword);
        setTimeout(() => closeProfileOverlay(), 2000);
      }
    })
    .catch(error => {
      console.error('Password update error:', error);
      document.getElementById('profileMessage').innerHTML = 'Update failed. Please try again.';
    });
  };
});