def retrieve_memories(
    query,
    memories,
    top_k=3
):

    if not memories:
        return []


    # 兼容 yaml 外层 memories
    if isinstance(memories, dict):

        memories = memories.get(
            "memories",
            []
        )


    query = query.lower()


    results = []


    for memory in memories:

        score = 0


        tags = memory.get(
            "tags",
            []
        )


        for tag in tags:

            if tag.lower() in query:
                score += 1


        if score > 0:

            results.append(
                (
                    score,
                    memory
                )
            )


    results.sort(
        key=lambda x:x[0],
        reverse=True
    )


    return [
        item[1]
        for item in results[:top_k]
    ]