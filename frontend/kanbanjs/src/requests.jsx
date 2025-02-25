export async function getUrl(yourUrl) {
  try {
    const response = await fetch(yourUrl);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching data:", error.message);
    throw error;
  }
}

export async function postUrl(yourUrl, postData = {}) {
  try {
    const response = await fetch(yourUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(postData),
    });
    if (!response.ok) {
      throw new Error(`POST request failed with status ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error posting data:", error.message);
    throw error;
  }
}

export async function deleteUrl(yourUrl, deleteData = null) {
  try {
    const options = {
      method: "DELETE",
    };

    if (deleteData !== null) {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify(deleteData);
    }

    const response = await fetch(yourUrl, options);
    if (!response.ok) {
      throw new Error(`DELETE request failed with status ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error deleting data:", error.message);
    throw error;
  }
}

export async function putUrl(yourUrl, putData = {}) {
  try {
    const response = await fetch(yourUrl, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(putData),
    });
    if (!response.ok) {
      throw new Error(`PUT request failed with status ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error updating data:", error.message);
    throw error;
  }
}
