package smart.document.backend.config;

import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.repeat.RepeatStatus;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;

@Configuration
public class DocumentBatchConfig {

    @Bean
    public Job documentProcessingJob(
            JobRepository jobRepository,
            Step documentProcessingStep) {

        return new JobBuilder(
                "documentProcessingJob",
                jobRepository
        )
                .start(documentProcessingStep)
                .build();
    }

    @Bean
    public Step documentProcessingStep(
            JobRepository jobRepository,
            PlatformTransactionManager transactionManager) {

        return new StepBuilder(
                "documentProcessingStep",
                jobRepository
        )
                .tasklet((contribution, chunkContext) -> {

                    System.out.println(
                            "Batch: Processing documents..."
                    );

                    return RepeatStatus.FINISHED;
                }, transactionManager)
                .build();
    }
}