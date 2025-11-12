CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(150) NOT NULL,
    description TEXT,
    event_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE registrations (
    registration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES events(event_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    attended BOOLEAN DEFAULT FALSE,
    registered_at TIMESTAMP DEFAULT now()
);

CREATE TABLE verification (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid().
    event_id UUID REFERENCES events(event_id) NOT NULL,
    user_id UUID REFERENCES users(user_id) NOT NULL,
    document_url TEXT NOT NULL,
    image_url TEXT NOT NULL
);