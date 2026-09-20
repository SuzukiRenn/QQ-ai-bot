def calculate_memory_emotion(memories):

    changes = {

        "happiness":0,
        "sadness":0,
        "anger":0,
        "nostalgia":0

    }


    for memory in memories:

        emotion = memory.get(
            "emotion",
            {}
        )


        for key,value in emotion.items():

            changes[key] += value


    return changes