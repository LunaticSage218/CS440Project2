async function fetchContacts() {
    const response = await fetch("/api/contacts");
    const contacts = await response.json();

    const list = document.getElementById("contactList");
    list.innerHTML = "";

    contacts.forEach(addContactToUI);
}

function addContactToUI(contact) {
    const div = document.createElement("div");
    div.className = "contact";
    div.id = `contact-${contact.id}`;

    const list = document.getElementById("contactList");

    div.innerHTML = `
        <div class="contact-info" id="info-${contact.id}">
            <strong>${contact.name}</strong> |
            ${contact.phone} |
            ${contact.address}
        </div>

        <div class="actions">
            <button onclick="startEdit(${contact.id}, '${contact.name}', '${contact.phone}', '${contact.address}')">Edit</button>
            <button onclick="deleteContact(${contact.id})">Delete</button>
        </div>
    `;

    list.appendChild(div);
}


function removeContactUI(id) {
    const el = document.getElementById(`contact-${id}`);
    if (el) el.remove();
}

function updateContactUI(c) {
    const info = document.getElementById(`info-${c.id}`);

    if (info) {
        info.innerHTML = `
            <strong>${c.name}</strong> |
            ${c.phone} |
            ${c.address}
        `;
    }
}

async function addContact() {
    const name = document.getElementById("name").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;

    await fetch("/api/contacts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, address })
    });

    document.getElementById("name").value = "";
    document.getElementById("phone").value = "";
    document.getElementById("address").value = "";
}

async function deleteContact(id) {
    await fetch(`/api/contacts/${id}`, {method: "DELETE"});
}

function startEdit(id, name, phone, address) {
    const infoDiv = document.getElementById(`info-${id}`);

    infoDiv.innerHTML = `
        <input class="edit-input" id="edit-name-${id}" value="${name}">
        <input class="edit-input" id="edit-phone-${id}" value="${phone}">
        <input class="edit-input" id="edit-address-${id}" value="${address}">
        <button onclick="saveEdit(${id})">Save</button>
        <button onclick="fetchContacts()">Cancel</button>
    `;
}

async function saveEdit(id) {
    const name = document.getElementById(`edit-name-${id}`).value;
    const phone = document.getElementById(`edit-phone-${id}`).value;
    const address = document.getElementById(`edit-address-${id}`).value;

    await fetch(`/api/contacts/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, address })
    });
}

const socket = new WebSocket("ws://localhost:8765");

socket.onopen = () => {
    console.log("WebSocket connected");
};

socket.onmessage = (event) => {
    console.log("Event received:", event.data);

    const data = JSON.parse(event.data);

    switch (data.event) {

        case "contact_added":
            addContactToUI(data.contact);
            break;

        case "contact_updated":
            updateContactUI(data.contact);
            break;

        case "contact_deleted":
            removeContactUI(data.id);
            break;
    }
};

fetchContacts();