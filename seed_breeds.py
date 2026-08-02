from app.db.session import SessionLocal
from app.models.dogs.dog_breed import DogBreed

BREEDS = [
    ("Labrador Retriever", 60, 100, 38.3, 38.7),
    ("Pastor Alemán", 60, 100, 38.3, 38.7),
    ("Bulldog Francés", 70, 120, 38.1, 38.5),
    ("Beagle", 60, 100, 38.1, 38.5),
    ("Chihuahua", 100, 140, 38.3, 38.7),
    ("Poodle (Caniche)", 60, 100, 38.3, 38.7),
    ("Rottweiler", 60, 100, 38.3, 38.7),
    ("Golden Retriever", 60, 100, 38.3, 38.7),
    ("Shih Tzu", 100, 140, 38.1, 38.5),
    ("Cocker Spaniel", 70, 120, 38.3, 38.7),
    ("Doberman Pinscher", 60, 100, 38.3, 38.7),
    ("Boxer", 60, 100, 38.3, 38.7),
    ("Dachshund", 100, 140, 38.1, 38.5),
    ("Pug", 70, 120, 38.3, 38.7),
    ("Shiba Inu", 70, 100, 38.3, 38.7),
    ("Schnauzer", 70, 120, 38.3, 38.7),
    ("Yorkshire Terrier", 100, 140, 38.1, 38.5),
    ("Maltés", 100, 140, 38.1, 38.5),
    ("Siberian Husky", 60, 100, 38.3, 38.7),
    ("Pomerania", 100, 140, 38.1, 38.5),
    ("Bulldog", 70, 120, 38.3, 38.7),
    ("Basset Hound", 60, 100, 38.3, 38.7),
    ("Cavalier King Charles Spaniel", 70, 120, 38.3, 38.7),
    ("Saint Bernard", 60, 100, 38.3, 38.7),
    ("Airedale Terrier", 60, 100, 38.3, 38.7),
    ("Alaskan Malamute", 60, 100, 38.3, 38.7),
    ("Border Collie", 60, 100, 38.3, 38.7),
    ("Collie", 60, 100, 38.3, 38.7),
    ("Shetland Sheepdog", 60, 100, 38.3, 38.7),
    ("American Pit Bull Terrier", 60, 100, 38.3, 38.7),
    ("English Setter", 60, 100, 38.3, 38.7),
    ("Jack Russell Terrier", 100, 140, 38.3, 38.7),
    ("Havanese", 100, 140, 38.3, 38.7),
    ("Samoyedo", 60, 100, 38.3, 38.7),
    ("Bichon Frisé", 100, 140, 38.3, 38.7),
    ("Weimaraner", 60, 100, 38.3, 38.7),
    ("Chow Chow", 60, 100, 38.3, 38.7),
    ("Bloodhound", 60, 100, 38.3, 38.7),
    ("Mastín Napolitano", 60, 100, 38.3, 38.7),
    ("Akita Inu", 60, 100, 38.3, 38.7),
    ("French Bulldog", 70, 120, 38.3, 38.7),
    ("Lhasa Apso", 100, 140, 38.3, 38.7),
    ("Australian Shepherd", 60, 100, 38.3, 38.7),
    ("Maltipoo", 100, 140, 38.3, 38.7),
    ("Papillon", 100, 140, 38.3, 38.7),
    ("Mastín Español", 60, 100, 38.3, 38.7),
    ("Rat Terrier", 100, 140, 38.3, 38.7),
    ("Pekingese", 100, 140, 38.3, 38.7),
    ("Newfoundland", 60, 100, 38.3, 38.7),
    ("Doberman", 60, 100, 38.3, 38.7),
    ("Puli", 60, 100, 38.3, 38.7),
    ("Cairn Terrier", 100, 140, 38.3, 38.7),
    ("Perro Mestizo", 60, 120, 38.3, 38.7),
]

db = SessionLocal()

for name, hr_min, hr_max, temp_min, temp_max in BREEDS:
    existing = db.query(DogBreed).filter(DogBreed.name == name).first()

    if not existing:
        db.add(
            DogBreed(
                name=name,
                heart_rate_min=hr_min,
                heart_rate_max=hr_max,
                temperature_min=temp_min,
                temperature_max=temp_max,
                is_active=True,
            )
        )

db.commit()
db.close()

print("Dog breeds seeded.")