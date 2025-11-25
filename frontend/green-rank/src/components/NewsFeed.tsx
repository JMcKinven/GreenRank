import React, { useEffect, useState } from "react";
import "./Newsfeed.css";

type NewsItem = {
    id: string | number;
    title: string;
    url: string;
    published_at?: string | null;
};

export default function NewsFeed() {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchNews() {
            try {
                const API_KEY = "pub_7e89af8004014743a2da545468dd0116"; // For dev only

                // NewsData.io endpoint
                const endpoint = `https://newsdata.io/api/1/news?apikey=${API_KEY}&q=(sustainability OR "climate change" OR "global warming" OR "renewable energy" OR "net zero")&category=environment&language=en&country=gb`;


                const res = await fetch(endpoint);
                if (!res.ok) throw new Error("Failed to fetch news");

                const data = await res.json();

                // NewsData.io returns articles inside "results"
                const raw = data.results ?? [];

                const normalized: NewsItem[] = raw.map((n: any) => ({
                    id: n.article_id ?? n.link ?? Math.random(),
                    title: n.title ?? "Untitled",
                    url: n.link ?? n.url ?? "#",
                    published_at: n.pubDate ?? n.pub_date ?? null,
                }));

                setNews(normalized);
            } catch (e) {
                console.error("Failed to load news:", e);
            } finally {
                setLoading(false);
            }
        }

        fetchNews();
    }, []);

    return (
        <div className="news-feed">
            <h2>Latest Sustainability News</h2>

            {loading && <div className="news-loading">Loading news…</div>}

            <ul>
                {news.map((item) => (
                    <li key={item.id}>
                        <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="news-headline"
                        >
                            {item.title}
                        </a>

                        {item.published_at && (
                            <div className="news-date">
                                {new Date(item.published_at).toLocaleDateString()}
                            </div>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
}
