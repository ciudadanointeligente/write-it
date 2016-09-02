exports.organizations = {
  dogs:{

    html_url: "https://",
    url: "https://",
    classification: "party",
    _id: "dogsfci",
    name: "Dogs fci",
    memberships: [
        {

          html_url: "https://dogsfci",
          url: "https://dogsfci",
          organization_id: "dogsfci",
          role: "Boss",
          start_date: "1987-03-21",
          end_date: "2007-03-20",
          person_id: "fiera-feroz",
          _id: "fieraBoss",
          links: [ ],
          contact_details: [ ]

      }
    ],
    posts: [ ],
    links: [ ],
    contact_details: [ ],
    identifiers: [ ],
    other_names:
    [

      {

          name: "Dogs",
          id: "54e314e82ec9128d32084466"

      }

    ]
  }
};
exports.persons = {
  raton: {
    _id: "raton-inteligente",
    name: "Ratón Inteligente",
    email: "raton@ciudadanoi.org",
  },
  fiera: {
    _id: "fiera-feroz",
    name: "Fiera Feroz",
    summary:"Fiera es una perra muy buena onda",
    email: "fiera@ciudadanointeligente.org",
    image:"http://www.ciudadanointeligente.org/wp-content/uploads/2012/05/fiera.jpg",
    contact_details:[
    {
      "id": "53b47e011fa1acd34505d9b3",
      "label": "email",
      "type": "email",
      "value": "fiera@ciudadanointeligente.org",
      "note": ""
    }
    ]
  },
  benito: {
    _id: "benito",
    name: "Benito",
    summary:"Benito es el perro de la Cata",
    image:"http://i.imgur.com/Vehnajb.jpg",
    email: "benito@ciudadanointeligente.org",
    contact_details:[
      {
        "id": "53b47e011fa1acd34505d9b3",
        "label": "email",
        "type": "email",
        "value": "benito@ciudadanointeligente.org",
        "note": ""
      }
    ]
  }
};
exports.memberships = {
  fieraBoss: {

      html_url: "https://dogsfci",
      url: "https://dogsfci",
      organization_id: "dogsfci",
      role: "Boss",
      start_date: "2011-03-21",
      person_id: "fiera-feroz",
      _id: "fieraBoss",
      links: [ ],
      contact_details: [ ]

  },
  fieraNotBoss: {

      html_url: "https://dogsfci",
      url: "https://dogsfci",
      organization_id: "dogsfci",
      role: "NotTheBoss",
      start_date: "2005-03-21",
      end_date: "2009-03-21",
      person_id: "fiera-feroz",
      _id: "fieraNotBoss",
      links: [ ],
      contact_details: [ ]

  },
  benitoBoss: {

      html_url: "https://dogsfci",
      url: "https://dogsfci",
      organization_id: "dogsfci",
      role: "Boss",
      start_date: "1987-03-21",
      end_date: "2007-03-20",
      person_id: "benito",
      _id: "benitoBoss",
      links: [ ],
      contact_details: [ ]

  },
  ratonNotBoss: {

      html_url: "https://ratonNotBoss",
      url: "https://ratonNotBoss",
      organization_id: "dogsfci",
      role: "NotTheBoss",
      start_date: "1987-03-21",
      end_date: "2045-03-20",
      person_id: "raton-inteligente",
      _id: "ratonNotBoss",
      links: [ ],
      contact_details: [ ]

  }
};
