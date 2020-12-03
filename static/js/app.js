function searchDocs(event){
	// console.log(event.target.val);
	event.preventDefault();
	let query = document.getElementById("search-input").value;

	if (query){
		axios.get('http://127.0.0.1:5000/search/' + query)
			.then( (res) => {
				const urls = res.data.results
				const responseTime = res.data.responseTime

				let resultsList = document.getElementById("results-list");
				resultsList.innerHTML = "";

				let resultCounter = 1

				for (let url of urls){
					let listItem = document.createElement("li");
					listItem.classList.add('list-group-item');
					listItem.innerHTML = `<b>${resultCounter}</b>. <a href="${url}">${url}</a>`;
					resultsList.appendChild(listItem);
					resultCounter++;
				}

				let responseTimeText = document.getElementById("response-time")
				responseTimeText.innerHTML = responseTime + " ms"
			})
			.catch( (error) => {
				console.log(error)
			})
	} 
}