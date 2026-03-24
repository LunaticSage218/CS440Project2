async function fetchContacts() {
    const response = await fetch("/api/contacts");
    const contacts = await response.json();

    const list = document.getElementById("contactList");
    list.innerHTML = "";

    contacts.forEach(c => {
        const div = document.createElement("div");
        div.className = "contact";
        div.id = `contact-${c.id}`;

        const safeName = String(c.name).replace(/'/g, "\\'");
        const safePhone = String(c.phone).replace(/'/g, "\\'");
        const safeAddress = String(c.address).replace(/'/g, "\\'");

        div.innerHTML = `
            <div class="contact-info" id="info-${c.id}">
                <strong>${c.name}</strong> |
                ${c.phone} |
                ${c.address}
            </div>
            <div class="actions">
                <button onclick="startEdit(${c.id}, '${safeName}', '${safePhone}', '${safeAddress}')">Edit</button>
                <button onclick="deleteContact(${c.id})">Delete</button>
            </div>
        `;

        list.appendChild(div);
    });
}

async function addContact() {
    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const address = document.getElementById("address").value.trim();

    if (!name || !phone || !address) {
        alert("Please fill in all fields.");
        return;
    }

    const response = await fetch("/api/contacts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, address })
    });

    if (!response.ok) {
        alert("Failed to add contact.");
        return;
    }

    document.getElementById("name").value = "";
    document.getElementById("phone").value = "";
    document.getElementById("address").value = "";

    fetchContacts();
}

async function deleteContact(id) {
    const response = await fetch(`/api/contacts/${id}`, { method: "DELETE" });

    if (!response.ok) {
        alert("Failed to delete contact.");
        return;
    }

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
    const name = document.getElementById(`edit-name-${id}`).value.trim();
    const phone = document.getElementById(`edit-phone-${id}`).value.trim();
    const address = document.getElementById(`edit-address-${id}`).value.trim();

    if (!name || !phone || !address) {
        alert("Please fill in all fields.");
        return;
    }

    const response = await fetch(`/api/contacts/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, address })
    });

    if (!response.ok) {
        alert("Failed to update contact.");
        return;
    }

    fetchContacts();
}

fetchContacts();
setInterval(fetchContacts, 2000);