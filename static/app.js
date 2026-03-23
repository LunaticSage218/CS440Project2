async function fetchContacts() {
    const response = await fetch("/api/contacts");
    const contacts = await response.json();

    const list = document.getElementById("contactList");
    list.innerHTML = "";

    contacts.forEach(c => {
        const div = document.createElement("div");
        div.className = "contact";
        div.id = `contact-${c.id}`;

        div.innerHTML = `
            <div class="contact-info" id="info-${c.id}">
                <strong>${c.name}</strong> |
                ${c.phone} |
                ${c.address}
            </div>
            <div class="actions">
                <button onclick="startEdit(${c.id}, '${c.name}', '${c.phone}', '${c.address}')">Edit</button>
                <button onclick="deleteContact(${c.id})">Delete</button>
            </div>
        `;

        list.appendChild(div);
    });
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

    fetchContacts();
}

async function deleteContact(id) {
    await fetch(`/api/contacts/${id}`, { method: "DELETE" });
    fetchContacts();
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

    fetchContacts();
}

fetchContacts();
