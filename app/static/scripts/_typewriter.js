// typewriter_effect = require("typewriter-effect")

async function getData() {
  const url = "/api/constructions";
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    console.log(json);
    return json
  } catch (error) {
    console.error(error.message);
  }
}

const main = async () => {
  var field = document.getElementById('typewriter');

  const constructions = await getData();

  console.log(typeof(constructions));
  console.log(constructions);

  const linked_constructions = Array.from(constructions).map(
    construction => `<a href="/construction/${construction.construction_id}">${construction.name}</a>`
  );

  console.log(`linked_constructions:`, linked_constructions);

  typewriter = new Typewriter(field, {
    strings: linked_constructions,
    autoStart: true,
    loop: true,
    pauseFor: 3500,
  });
}

main()